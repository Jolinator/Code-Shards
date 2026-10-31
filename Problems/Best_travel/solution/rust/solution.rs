fn subsets(ls: &Vec<i32>, k: usize) -> Vec<Vec<usize>>{
    let mut subsets = vec![];
    let mut cycle_vec = vec![];
    for i in 0..k{
        cycle_vec.push(i)
    }
    
    loop{
        let mut outbreak = 0;
        let values: Vec<_> = cycle_vec.iter()
        .map(|&ind| ls[ind] as usize)
        .collect();
        
        
        subsets.push(values);
        let mut index = cycle_vec.len()-1;
        let mut reverse_index;
        
        loop {
            reverse_index = cycle_vec.len() - (index + 1);
            if cycle_vec[index] + 1 >= ls.len() - reverse_index{
                cycle_vec[index] = 0;
            }
            else {
                cycle_vec[index] += 1;
                break;
            }
            if index == 0{
                outbreak = 1;
                
                break;
            }
            index -= 1
        }
        
        if outbreak == 1 {
            break;
        }
        
        for ind in 0..cycle_vec.len()-1{
            if cycle_vec[ind+1] <= cycle_vec[ind]{
                cycle_vec[ind+1] = cycle_vec[ind] +1; 
            }
        }
        
    }
    
    subsets
}

fn sum(ls: Vec<usize>) -> usize{
    let mut sum = 0;
    for i in ls{
        sum += i;
    }
    sum
}

fn choose_best_sum(t: i32, k: i32, ls: &Vec<i32>) -> i32 {
    if k as usize > ls.len() {
        
        return -1
    }
    
    let mut best_distance:i32 = -1;
    
    let s_sets = subsets(ls, k as usize);
    
    for set in s_sets {
        let sum_of_set = sum(set) as i32;
        if sum_of_set > best_distance && sum_of_set <= t {
            best_distance = sum_of_set;
        }
    }
    best_distance
}