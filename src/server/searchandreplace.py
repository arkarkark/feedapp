# Copyright 2011 Alex K (wtwf.com)

def SplitEscapable(s, sep):
  ans = []
  idx = 0
  for x in s.split(sep):
    if len(ans) == idx:
      ans.append(x)
    else:
      ans[idx] += sep + x
    if x.endswith('\\'):
      ans[idx] = ans[idx][0:-1]
    else:
      idx += 1
  return ans
