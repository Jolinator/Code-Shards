#!/usr/bin/env bash

# Collect Linux host details that are useful when tuning low-level code.
# Usage: bash collect_linux.sh [output.env]
set -u

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
output_file="${1:-${script_dir}/.env}"
output_dir="$(dirname -- "$output_file")"
mkdir -p -- "$output_dir" || exit 1
tmp_file="${output_file}.tmp.$$"
trap 'rm -f -- "$tmp_file"' EXIT
: > "$tmp_file" || exit 1

env_put() {
    local key="$1"
    local value="${2:-}"
    [[ -n "$value" ]] || return 0
    value=${value//\\/\\\\}
    value=${value//\"/\\\"}
    value=${value//$'\r'/\\r}
    value=${value//$'\n'/\\n}
    printf '%s="%s"\n' "$key" "$value" >> "$tmp_file"
}

first_cpu_value() {
    local key="$1"
    awk -F: -v key="$key" '$1 ~ "^[[:space:]]*" key "[[:space:]]*$" { sub(/^[[:space:]]+/, "", $2); print $2; exit }' /proc/cpuinfo 2>/dev/null
}

read_value() {
    local path="$1"
    if [[ -r "$path" ]]; then
        tr -d '\n' < "$path"
    fi
}

logical_cores="$(getconf _NPROCESSORS_ONLN 2>/dev/null || printf '%s' "$(grep -c '^processor[[:space:]]*:' /proc/cpuinfo 2>/dev/null || true)")"
logical_cores="${logical_cores//[[:space:]]/}"
physical_cores="$(
    shopt -s nullglob
    for cpu_dir in /sys/devices/system/cpu/cpu[0-9]*; do
        [[ -d "$cpu_dir/topology" ]] || continue
        if [[ -r "$cpu_dir/online" ]] && [[ "$(read_value "$cpu_dir/online")" == "0" ]]; then
            continue
        fi
        package="$(read_value "$cpu_dir/topology/physical_package_id")"
        core="$(read_value "$cpu_dir/topology/core_id")"
        [[ -n "$package" && -n "$core" ]] && printf '%s:%s\n' "$package" "$core"
    done | sort -u | wc -l | tr -d '[:space:]'
)"
socket_count="$(
    shopt -s nullglob
    for package_file in /sys/devices/system/cpu/cpu[0-9]*/topology/physical_package_id; do
        printf '%s\n' "$(read_value "$package_file")"
    done | sort -u | wc -l | tr -d '[:space:]'
)"

cpu_flags="$(first_cpu_value flags)"
[[ -n "$cpu_flags" ]] || cpu_flags="$(first_cpu_value Features)"

cache_details=""
cache_sharing_map=""
l1d_size=""
l1i_size=""
l1u_size=""
l2_size=""
l3_size=""
l1_n_ways=""
l2_n_ways=""
l3_n_ways=""
l1d_set_counts=""
l1i_set_counts=""
l1u_set_counts=""
l2_set_counts=""
l3_set_counts=""
l1d_instance_count=0
l1i_instance_count=0
l1u_instance_count=0
l2_instance_count=0
l3_instance_count=0
cache_line_sizes=""
declare -A cache_group_labels=()
shopt -s nullglob
for cache_dir in /sys/devices/system/cpu/cpu[0-9]*/cache/index*; do
    [[ -d "$cache_dir" ]] || continue
    level="$(read_value "$cache_dir/level")"
    type="$(read_value "$cache_dir/type")"
    size="$(read_value "$cache_dir/size")"
    size_kb="$(awk -v value="$size" 'BEGIN { unit=substr(value,length(value)); amount=substr(value,1,length(value)-1)+0; if (unit=="K") printf "%.0f", amount; else if (unit=="M") printf "%.0f", amount*1024; else if (unit=="G") printf "%.0f", amount*1048576; else printf "%.0f", value/1024 }')"
    line_size="$(read_value "$cache_dir/coherency_line_size")"
    ways="$(read_value "$cache_dir/ways_of_associativity")"
    set_count="$(read_value "$cache_dir/number_of_sets")"
    shared="$(read_value "$cache_dir/shared_cpu_list")"
    [[ -n "$level" && -n "$type" && -n "$size" ]] || continue

    case "$type" in
        Data) type_short="d" ;;
        Instruction) type_short="i" ;;
        Unified) type_short="u" ;;
        *) type_short="other" ;;
    esac
    entry="L${level}${type_short}:${size_kb}KB"
    [[ -n "$line_size" ]] && entry+="/${line_size}B-line"
    [[ -n "$ways" && "$ways" != "0" ]] && entry+="/${ways}-way"
    [[ -n "$set_count" && "$set_count" != "0" ]] && entry+="/${set_count}-sets"
    group_key="${level}|${type}|${size}|${line_size}|${ways}|${set_count}|${shared}"
    [[ -n "$shared" ]] && entry+="/shared=${shared}"
    cache_group_labels["$group_key"]="$entry"
    [[ -n "$shared" ]] && cache_sharing_map+="L${level}:${shared}"$'\n'
    [[ -n "$line_size" ]] && cache_line_sizes+="${line_size}"$'\n'
    if [[ "$ways" =~ ^[1-9][0-9]*$ ]]; then
        case "$level" in
            1) l1_n_ways+="${ways}"$'\n' ;;
            2) l2_n_ways+="${ways}"$'\n' ;;
            3) l3_n_ways+="${ways}"$'\n' ;;
        esac
    fi
    if [[ "$set_count" =~ ^[1-9][0-9]*$ ]]; then
        case "${level}:${type}" in
            1:Data) l1d_set_counts+="${set_count}"$'\n' ;;
            1:Instruction) l1i_set_counts+="${set_count}"$'\n' ;;
            1:Unified) l1u_set_counts+="${set_count}"$'\n' ;;
            2:*) l2_set_counts+="${set_count}"$'\n' ;;
            3:*) l3_set_counts+="${set_count}"$'\n' ;;
        esac
    fi

    case "${level}:${type}" in
        1:Data) l1d_size+="${size_kb}"$'\n' ;;
        1:Instruction) l1i_size+="${size_kb}"$'\n' ;;
        1:Unified) l1u_size+="${size_kb}"$'\n' ;;
        2:*) l2_size+="${size_kb}"$'\n' ;;
        3:*) l3_size+="${size_kb}"$'\n' ;;
    esac
done
for group_key in "${!cache_group_labels[@]}"; do
    cache_details+="${cache_group_labels[$group_key]}"$'\n'
done
cache_details="$(printf '%s' "$cache_details" | sort | paste -sd';' -)"
cache_sharing_map="$(printf '%s' "$cache_sharing_map" | sort -u | paste -sd';' -)"
cache_line_sizes="$(printf '%s' "$cache_line_sizes" | sort -nu | paste -sd, -)"
l1d_size="$(printf '%s' "$l1d_size" | sort -u | paste -sd, -)"
l1i_size="$(printf '%s' "$l1i_size" | sort -u | paste -sd, -)"
l1u_size="$(printf '%s' "$l1u_size" | sort -u | paste -sd, -)"
l2_size="$(printf '%s' "$l2_size" | sort -u | paste -sd, -)"
l3_size="$(printf '%s' "$l3_size" | sort -u | paste -sd, -)"
l1_n_ways="$(printf '%s' "$l1_n_ways" | sort -nu | paste -sd, -)"
l2_n_ways="$(printf '%s' "$l2_n_ways" | sort -nu | paste -sd, -)"
l3_n_ways="$(printf '%s' "$l3_n_ways" | sort -nu | paste -sd, -)"
l1d_set_counts="$(printf '%s' "$l1d_set_counts" | sort -nu | paste -sd, -)"
l1i_set_counts="$(printf '%s' "$l1i_set_counts" | sort -nu | paste -sd, -)"
l1u_set_counts="$(printf '%s' "$l1u_set_counts" | sort -nu | paste -sd, -)"
l2_set_counts="$(printf '%s' "$l2_set_counts" | sort -nu | paste -sd, -)"
l3_set_counts="$(printf '%s' "$l3_set_counts" | sort -nu | paste -sd, -)"
for group_key in "${!cache_group_labels[@]}"; do
    IFS='|' read -r group_level group_type _ <<< "$group_key"
    case "${group_level}:${group_type}" in
        1:Data) ((l1d_instance_count+=1)) ;;
        1:Instruction) ((l1i_instance_count+=1)) ;;
        1:Unified) ((l1u_instance_count+=1)) ;;
        2:*) ((l2_instance_count+=1)) ;;
        3:*) ((l3_instance_count+=1)) ;;
    esac
done

cpu_max_mhz=""
cpu_cur_mhz="$(first_cpu_value 'cpu MHz')"
for policy_dir in /sys/devices/system/cpu/cpufreq/policy[0-9]*; do
    [[ -r "$policy_dir/scaling_max_freq" ]] || continue
    cpu_max_mhz+="$(awk '{printf "%.0f", $1/1000}' "$policy_dir/scaling_max_freq" 2>/dev/null)"$'\n'
done
if [[ -z "$cpu_max_mhz" && -r /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq ]]; then
    cpu_max_mhz="$(awk '{printf "%.0f", $1/1000}' /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq 2>/dev/null)"
fi
if [[ -r /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq ]]; then
    cpu_cur_mhz="$(awk '{printf "%.0f", $1/1000}' /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null)"
fi
cpu_max_mhz="$(printf '%s' "$cpu_max_mhz" | sort -nu | paste -sd, -)"

mem_total_kb="$(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo 2>/dev/null)"
mem_available_kb="$(awk '/^MemAvailable:/ {print $2; exit}' /proc/meminfo 2>/dev/null)"
swap_total_kb="$(awk '/^SwapTotal:/ {print $2; exit}' /proc/meminfo 2>/dev/null)"
swap_free_kb="$(awk '/^SwapFree:/ {print $2; exit}' /proc/meminfo 2>/dev/null)"
swap_used_kb="$(awk '/^SwapTotal:/ {total=$2} /^SwapFree:/ {free=$2} END {if (total != "" && free != "") print total-free}' /proc/meminfo 2>/dev/null)"
vm_commit_limit_kb="$(awk '/^CommitLimit:/ {print $2; exit}' /proc/meminfo 2>/dev/null)"
vm_committed_kb="$(awk '/^Committed_AS:/ {print $2; exit}' /proc/meminfo 2>/dev/null)"
hugepage_size_kb="$(awk '/^Hugepagesize:/ {print $2; exit}' /proc/meminfo 2>/dev/null)"
page_size_bytes="$(getconf PAGE_SIZE 2>/dev/null || true)"
numa_node_count="$(find /sys/devices/system/node -maxdepth 1 -type d -name 'node[0-9]*' 2>/dev/null | wc -l | tr -d '[:space:]')"
numa_cpu_map="$(
    shopt -s nullglob
    for node_dir in /sys/devices/system/node/node[0-9]*; do
        [[ -r "$node_dir/cpulist" ]] && printf '%s:%s; ' "${node_dir##*/}" "$(read_value "$node_dir/cpulist")"
    done
)"
numa_cpu_map="${numa_cpu_map%; }"

hypervisor="no"
if grep -m1 -Eq '(^|[[:space:]])hypervisor([[:space:]]|$)' /proc/cpuinfo 2>/dev/null; then
    hypervisor="yes"
fi
if command -v systemd-detect-virt >/dev/null 2>&1; then
    detected_virt="$(systemd-detect-virt --vm 2>/dev/null || true)"
    [[ -n "$detected_virt" && "$detected_virt" != "none" ]] && hypervisor="$detected_virt"
fi

smt_active="unavailable"
if [[ -r /sys/devices/system/cpu/smt/active ]]; then
    [[ "$(read_value /sys/devices/system/cpu/smt/active)" == "1" ]] && smt_active="yes" || smt_active="no"
elif [[ -n "$logical_cores" && -n "$physical_cores" ]]; then
    (( logical_cores > physical_cores )) && smt_active="yes" || smt_active="no"
fi

cpu_governor="$(read_value /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
thp_mode="$(read_value /sys/kernel/mm/transparent_hugepage/enabled)"
security_mitigations=""
for mitigation_file in /sys/devices/system/cpu/vulnerabilities/*; do
    [[ -r "$mitigation_file" ]] || continue
    mitigation_value="$(read_value "$mitigation_file")"
    [[ -n "$security_mitigations" ]] && security_mitigations+="; "
    security_mitigations+="${mitigation_file##*/}=${mitigation_value}"
done

gpu_devices="unavailable (install lspci to enumerate)"
if command -v lspci >/dev/null 2>&1; then
    gpu_devices="$(lspci -mm 2>/dev/null | awk 'tolower($0) ~ /vga compatible controller|3d controller|display controller/ {gsub(/[[:space:]]+/, " "); printf "%s%s", sep, $0; sep="; "}')"
    [[ -n "$gpu_devices" ]] || gpu_devices="none reported by lspci"
fi
ssd_devices=""
hdd_devices=""
other_storage_devices=""
if command -v lsblk >/dev/null 2>&1; then
    while IFS= read -r name; do
        [[ -n "$name" ]] || continue
        device="/dev/${name}"
        device_type="$(lsblk -dnro TYPE -- "$device" 2>/dev/null || true)"
        [[ "$device_type" == "disk" ]] || continue
        rotational="$(lsblk -dnro ROTA -- "$device" 2>/dev/null || true)"
        capacity="$(lsblk -dnro SIZE -- "$device" 2>/dev/null || true)"
        model="$(lsblk -dnro MODEL -- "$device" 2>/dev/null | sed 's/[[:space:]]*$//' || true)"
        transport="$(lsblk -dnro TRAN -- "$device" 2>/dev/null | sed 's/[[:space:]]*$//' || true)"
        detail="${device}"
        [[ -n "$model" ]] && detail+=" (model=${model}"
        if [[ -n "$model" ]]; then
            [[ -n "$capacity" ]] && detail+=", size=${capacity}"
            [[ -n "$transport" ]] && detail+=", transport=${transport}"
            detail+=")"
        else
            [[ -n "$capacity" ]] && detail+=" (size=${capacity}"
            [[ -n "$transport" ]] && detail+=", transport=${transport}"
            [[ -n "$capacity" || -n "$transport" ]] && detail+=")"
        fi
        case "$rotational" in
            0) ssd_devices+="${detail}; " ;;
            1) hdd_devices+="${detail}; " ;;
            *) other_storage_devices+="${detail} (media type unknown); " ;;
        esac
    done < <(lsblk -dnro NAME 2>/dev/null)
    ssd_devices="${ssd_devices%; }"
    hdd_devices="${hdd_devices%; }"
    other_storage_devices="${other_storage_devices%; }"
    [[ -n "$ssd_devices" ]] || ssd_devices="none detected by lsblk"
    [[ -n "$hdd_devices" ]] || hdd_devices="none detected by lsblk"
else
    ssd_devices="unavailable (install util-linux for lsblk)"
    hdd_devices="unavailable (install util-linux for lsblk)"
fi

env_put CPU_ARCH "$(uname -m 2>/dev/null)"
env_put CPU_VENDOR "$(first_cpu_value vendor_id)"
env_put CPU_MODEL "$(first_cpu_value 'model name')"
env_put CPU_FAMILY "$(first_cpu_value 'cpu family')"
env_put CPU_MODEL_ID "$(first_cpu_value model)"
env_put CPU_STEPPING "$(first_cpu_value stepping)"
env_put CPU_MICROCODE "$(first_cpu_value microcode)"
env_put CPU_SOCKET_COUNT "$socket_count"
env_put CPU_PHYSICAL_CORES "$physical_cores"
env_put CPU_LOGICAL_CORES "$logical_cores"
env_put CPU_SMT_ACTIVE "$smt_active"
env_put CPU_MAX_MHZ "$cpu_max_mhz"
env_put CPU_CURRENT_MHZ "$cpu_cur_mhz"
env_put CPU_VIRTUALIZATION "$hypervisor"
env_put CPU_INSTRUCTION_FLAGS "$cpu_flags"
env_put CPU_CACHE_LINE_SIZE_BYTES "$cache_line_sizes"
env_put CPU_L1D_CACHE_SIZE_KB "$l1d_size"
env_put CPU_L1I_CACHE_SIZE_KB "$l1i_size"
env_put CPU_L1_UNIFIED_CACHE_SIZE_KB "$l1u_size"
env_put CPU_L2_CACHE_SIZE_KB "$l2_size"
env_put CPU_L3_CACHE_SIZE_KB "$l3_size"
env_put CPU_L1D_CACHE_SIZE_PER_INSTANCE_KB "$l1d_size"
env_put CPU_L1I_CACHE_SIZE_PER_INSTANCE_KB "$l1i_size"
env_put CPU_L1_UNIFIED_CACHE_SIZE_PER_INSTANCE_KB "$l1u_size"
env_put CPU_L2_CACHE_SIZE_PER_INSTANCE_KB "$l2_size"
env_put CPU_L3_CACHE_SIZE_PER_INSTANCE_KB "$l3_size"
env_put CPU_L1_N_WAY "$l1_n_ways"
env_put CPU_L2_N_WAY "$l2_n_ways"
env_put CPU_L3_N_WAY "$l3_n_ways"
env_put CPU_L1D_CACHE_SET_COUNT_PER_INSTANCE "$l1d_set_counts"
env_put CPU_L1I_CACHE_SET_COUNT_PER_INSTANCE "$l1i_set_counts"
env_put CPU_L1_UNIFIED_CACHE_SET_COUNT_PER_INSTANCE "$l1u_set_counts"
env_put CPU_L2_CACHE_SET_COUNT_PER_INSTANCE "$l2_set_counts"
env_put CPU_L3_CACHE_SET_COUNT_PER_INSTANCE "$l3_set_counts"
env_put CPU_L1D_CACHE_INSTANCE_COUNT "$l1d_instance_count"
env_put CPU_L1I_CACHE_INSTANCE_COUNT "$l1i_instance_count"
env_put CPU_L1_UNIFIED_CACHE_INSTANCE_COUNT "$l1u_instance_count"
env_put CPU_L2_CACHE_INSTANCE_COUNT "$l2_instance_count"
env_put CPU_L3_CACHE_INSTANCE_COUNT "$l3_instance_count"
env_put CPU_CACHE_TOPOLOGY "$cache_details"
env_put CPU_CACHE_SHARING_MAP "$cache_sharing_map"
env_put PHYSICAL_MEMORY_TOTAL_KB "$mem_total_kb"
env_put PHYSICAL_MEMORY_AVAILABLE_KB "$mem_available_kb"
env_put VIRTUAL_MEMORY_COMMIT_LIMIT_KB "$vm_commit_limit_kb"
env_put VIRTUAL_MEMORY_COMMITTED_KB "$vm_committed_kb"
env_put VIRTUAL_MEMORY_BACKING_TOTAL_KB "$swap_total_kb"
env_put VIRTUAL_MEMORY_BACKING_FREE_KB "$swap_free_kb"
env_put VIRTUAL_MEMORY_BACKING_USED_KB "$swap_used_kb"
env_put PAGE_SIZE_BYTES "$page_size_bytes"
env_put HUGEPAGE_SIZE_KB "$hugepage_size_kb"
env_put TRANSPARENT_HUGEPAGE_MODE "$thp_mode"
env_put CPU_NUMA_NODE_COUNT "$numa_node_count"
env_put CPU_NUMA_NODE_CPU_MAP "$numa_cpu_map"
env_put CPU_GOVERNOR "$cpu_governor"
env_put CPU_SECURITY_MITIGATIONS "$security_mitigations"
env_put GPU_DEVICES "$gpu_devices"
env_put SSD_DEVICES "$ssd_devices"
env_put HDD_DEVICES "$hdd_devices"
env_put OTHER_STORAGE_DEVICES "$other_storage_devices"

mv -f -- "$tmp_file" "$output_file" || exit 1
trap - EXIT
printf 'Wrote system details to %s\n' "$output_file"
