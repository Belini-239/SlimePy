global cur, cnt_left: number
global iter: number
{
    if (iter <= 1)
    {
        cur = 1
        cnt_left = 10
    }

    if (cnt_left > 0)
    {
        cur = cur * cnt_left
        cnt_left = cnt_left - 1
    }

    iter = iter + 1

    print(cur)
    print(cnt_left)
    print(iter)
}