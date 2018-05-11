import os

cur_dir = os.path.abspath(os.curdir)

picture_dirname = 'artist_work'
picture_dir_path = os.path.join(cur_dir, picture_dirname)

db_dirname = 'sqlite3'
db_name = 'pixiv.sqlite3'
db_path = os.path.join(cur_dir, db_dirname, db_name)


# class Solution:
#     def maxProfit(self, prices):
#         """
#         :type prices: List[int]
#         :rtype: int
#         """
#         min_list = []
#         min_temp = max(prices, default=0)  # 这里其实只是想设置一个比较大的初始值
#         for x in prices:
#             if min_temp > x:
#                 min_temp = x
#             min_list.append(min_temp)  # 建造一个最小值的List, 否则会超时
#         data_list = []
#         for index, data in enumerate(prices):
#             if index != 0:
#                 data_list.append(data - min_list[index - 1])
#             else:
#                 data_list.append(0)  # 防止越界
#         max_profit = max(data_list, default=0)
#         return max_profit if max_profit > 0 else 0
#
#
# if __name__ == '__main__':
#     x = Solution()
#     k = x.maxProfit([7, 1, 5, 3, 6, 4])

# class Solution:
#     def minimumDeleteSum(self, s1, s2):
#         """
#         :type s1: str
#         :type s2: str
#         :rtype: int
#         """
#         # 最大公共子串的变种
#         len_s1 = len(s1)
#         len_s2 = len(s2)
#         dp = [[] for _ in range(len_s1 + 1)]
#         dp[0].append(0)
#         for j in range(len_s2):
#             dp[0].append(dp[0][j] + ord(s2[j]))
#         for i in range(1, len_s1 + 1):
#             dp[i].append(dp[i - 1][0] + ord(s1[i - 1]))  # 一系列的初始化
#
#         for i in range(1, len_s1 + 1):
#             for j in range(1, len_s2 + 1):
#                 if s1[i] == s2[j]:
#                     dp[i].append(dp[i - 1][j - 1])
#                 else:
#                     dp[i].append(min(dp[i - 1][j] + ord(s1[i]), dp[i][j - 1] + ord(s2[j])))
#
#         return dp[len_s1][len_s2]
#
#
# x = Solution()
# s = x.minimumDeleteSum('ab', 'cde')
# s1 = 'ab'
# s2 = 'cde'
# cost = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
# print(cost)

# cost = [[0] * 10 for x in range(4)]
# print(cost)
# from pprint import pprint
#
# pprint(cost)

# import asyncio
#
#
# async def coroutine():
#     print('in coroutine.')
#     return 'result'
#
#
# event_loop = asyncio.get_event_loop()
# try:
#     return_value = event_loop.run_until_complete(
#         coroutine()
#     )
#     print('it returned: {!r}'.format(return_value))
# finally:
#     event_loop.close()

# import asyncio
#
# async def phase1():
#     print('in phase1')
#     return 'result1'
#
# async def phase2(arg):
#     print('in phase2')
#     return 'result derived from {}'.format(arg)
#
# async def outer():
#     print('in outer')
#     print('waiting for result1')
#     result1 = await phase1()
#     print('waiting for result2')
#     result2 = await phase2(result1)
#     return (result1, result2)
#
# event_loop = asyncio.get_event_loop()
# try:
#     result_value = event_loop.run_until_complete(outer())
#     print('result value: {!r}'.format(result_value))
# finally:
#     event_loop.close()

# import asyncio
# import functools
#
#
# def callback(arg, *, kwarg='default'):
#     print('callback invoked with {} and {}'.format(arg, kwarg))
#
#
# async def main(loop):
#     print('registering callbacks')
#     loop.call_soon(callback, 1)
#     wrapped = functools.partial(callback, kwarg='not default')
#     loop.call_soon(wrapped, 2)

# with open('ggg', 'r+t') as f:
#     print(f)
#     while True:
#         offset = f.tell()
#         x = f.readline()
#         if 'text' in x:
#             offset += x.index('text')
#             f.seek(offset)
#             f.write('good')
#         if not x:
#             break
