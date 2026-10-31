def fizzbuzz_plusplus(nums, words):
    limit = 1
    for n in nums: limit *= n
    rlist = []
    for i in range(1,limit+1):
        fword = ""
        for n in range(len(nums)):
            if i % nums[n] == 0:
                fword += words[n]
        if fword:
            rlist.append(fword)
        else:
            rlist.append(i)
    return rlist