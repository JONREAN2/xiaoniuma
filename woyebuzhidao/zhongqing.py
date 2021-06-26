#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

# 此脚本参考 https://github.com/Sunert/Scripts/blob/master/Task/youth.js

import traceback
import time
import re
import json
import sys
import os
from util import send, requests_session
from datetime import datetime, timezone, timedelta

# YOUTH_HEADER 为对象, 其他参数为字符串，自动提现需要自己抓包
# 选择微信提现30元，立即兑换，在请求包中找到withdraw2的请求，拷贝请求body类型 p=****** 的字符串，放入下面对应参数即可
# 分享一篇文章，找到 put.json 的请求，拷贝请求体，放入对应参数
cookies1 = {
  'YOUTH_HEADER': {"Accept-Encoding":"gzip, deflate, br","Cookie":"Hm_lvt_268f0a31fc0d047e5253dd69ad3a4775=1616600935,1616600941,1616600976,1616600982; Hm_lvt_6c30047a5b80400b0fd3f410638b8f0c=1616600310,1616600368,1616600942,1616600982; sensorsdata2019jssdkcross=%7B%22distinct_id%22%3A%2253327873%22%2C%22%24device_id%22%3A%2217864de740bacb-0501215fd7ec32-754c1651-370944-17864de740cbf8%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2217864de740bacb-0501215fd7ec32-754c1651-370944-17864de740cbf8%22%7D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2253327873%22%2C%22%24device_id%22%3A%2217864de86a47d1-0d59a6d4c1d2a38-754c1651-370944-17864de86a5ef4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2217864de86a47d1-0d59a6d4c1d2a38-754c1651-370944-17864de86a5ef4%22%7D; sajssdk_2015_cross_new_user=1; sajssdk_2019_cross_new_user=1","Connection":"keep-alive","Content-Type":"","Accept":"*/*","Host":"kd.youth.cn","User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148","Referer":"https://kd.youth.cn/h5/20190301taskcenter/ios/index.html?uuid=848fd169d2c54f95d562bdd9968d197e&sign=c960c15224635b917425a173454e5d52&channel_code=80000000&uid=53327873&channel=80000000&access=WIfI&app_version=1.8.2&device_platform=iphone&cookie_id=9f7fce68799cf315579e7486f9474642&openudid=848fd169d2c54f95d562bdd9968d197e&device_type=1&device_brand=iphone&sm_device_id=20210128174048a433e0d65b118d07ac8d99a1e0d03fa6017273224847e73f&device_id=50064191&version_code=182&os_version=14.1&cookie=MDAwMDAwMDAwMJCMpN-w09Wtg5-Bb36eh6CPqHualq2jmrCarWOw3YGyhbKcma7eqmqXr6NthJl7mI-shMmXeqDau4StacS3o7GFonqYr7nIqoKJl7CEY2Ft&device_model=iPhone_6_Plus&subv=1.5.1&&cookie=MDAwMDAwMDAwMJCMpN-w09Wtg5-Bb36eh6CPqHualq2jmrCarWOw3YGyhbKcma7eqmqXr6NthJl7mI-shMmXeqDau4StacS3o7GFonqYr7nIqoKJl7CEY2Ft&cookie_id=9f7fce68799cf315579e7486f9474642","Accept-Language":"zh-cn","X-Requested-With":"XMLHttpRequest"},
  'YOUTH_READBODY': 'p=9NwGV8Ov71o%3DgW5NEpb6rjb84bkaCQyOq-myT0C-Ktb_mEtDEGsOrBruuZzIpWlevTEf2n4e6SDtwtHI8jh7tGLFm1iscPtbZwlhO1--2rPMqEVay5SHQZ0Xa5om9y_QnFioIoDSg-ArtrfwznZt1IhRAOspLNm4F1Z4mRILDUTDM9AS-u45jBCEif5kxttnp7gTZq1mvyjMssqrAJBR4KGjHyn7BZEMPchCZuy8DE0uD7GBzr3uIWKyQLMa56PUeJDJ7zgx9zYN56SWoTfFCtKKDhhdw3JpvS9UV2XSIaA7V_hI4rYbZ8JbmBhaG92Fe8_u8AzZ3RNCYXjZGjaw4iAk0J-qtFCo0BHWONzvrkLM2B-RyRQazXVPIZEbE4-k9o1ZuzNzYbIeY1-uzcXh3xQqvAk0iqhJdJR1QBitRuJrtI8vdEAuBEFzyKaWYnQ9pBQ3hUJvMhyD1-7q6c-CyJe_Yu1BOH_vtEGrYgKjEOcUdciv4pBFIl2PRaaxkllzntD5-1JyFRemWGNoS7jW4GLXAz2tafyAP0lRV3KItEfjw3w1nQLQXQ94o_namVehbRB3r_bbuyFPLZa9gfzjKwLc3pl1TvBAPz-VZwJkyK82X1DUZ8nn1KqWLXIOhoargWzEI4etrQXNmT5_XsbmqPO9a0WzbgtmtpsV3MLS2vLAzt_V4pnH0d2t1jLCdnzs2wGovQtrxJdHZGeo90v0LorqMdWaIlZAQAualxt_WM9vtGsxzg8AQa35D4iWydOXY-JgF5RZXeyyjkJw9yGRqU7glv53c3w2f3OLIH3Fs-qmRnAmKouPa6hOLyq02ckveJLQWl6c_OEFzeKOuo1DJr02k0On1e0xbQ%3D%3D',
  'YOUTH_REDBODY': 'p=9NwGV8Ov71o%3DgW5NEpb6rjb84bkaCQyOq-myT0C-Ktb_mEtDEGsOrBruuZzIpWlevTEf2n4e6SDtwtHI8jh7tGLFm1iscPtbZwlhO1--2rPMqEVay5SHQZ0Xa5om9y_QnFioIoDSg-ArtrfwznZt1IhRAOspLNm4F1Z4mRILDUTDM9AS-u45jBCEif5kxttnp7gTZq1mvyjMssqrAJBR4KGjHyn7BZEMPchCZuy8DE0uD7GBzr3uIWKyQLMa56PUeJDJ7zgx9zYN56SWoTfFCtKKDhhdw3JpvRQMpwACqLsLNXkbp1o9f55oTnIil3gp6BMVBDPnKRzw2aTrxKS0VMZrywDJYIJT4jCbiAhbd8MFuQNXwutcO5dnrsyzUrReBhkxeZZIKi4tpeVjC-9kuXqBVbR8FxjEDEhmJTho2lkraqW71dm2rsKrTZuq9yF2qOwzoLlotIlEsH-U6Yjy4v40rqEgMuWPWYf6diMUg9gRs-lHhaabuwgEPNtvsfV4KoplZaO9t7wF2PMsWOZniCIAbWOISoTWRMF4NXyFwnaZ2aLM0l4Kq-R1gQd6eiCGmwOUvEYc-VHwn8Syr4Lynj4M3Ns980JuUMpvbKxN69e7KN5SJ0AsXJuWpekdPlFpUeFtoUEjmdD4P-BxjIF3KuHyaud8OS-1EwikiZNA6Hl1sy55PxmFoLsCw5mqryFkCde-TAea45DV11GDiLSagN8NQG68_n0pGXv5UBUTBkisWmDVvAhBorMTZ-YYxMiYCqBapjUqrA39wWRVx5m8WKd68xf5lH1F2_dRfGsiNI2cto4S_uku3i8AXpLTEF49nXpjhz0t3oTtdRZBrQz7x7ToqKRrRJBHWw%3D%3D',  
  'YOUTH_READTIMEBODY': 'p=9NwGV8Ov71o%3DgW5NEpb6rjb84bkaCQyOq-myT0C-Ktb_mEtDEGsOrBruuZzIpWlevTEf2n4e6SDtwtHI8jh7tGLFm1iscPtbZwlhO1--2rPMqEVay5SHQZ0Xa5om9y_QnFioIoDSg-ArtrfwznZt1IhRAOspLNm4F1Z4mRILDUTDM9AS-u45jBCEif5kxttnp7gTZq1mvyjMssqrAJBR4KGjHyn7BZEMPchCZuy8DE0uD7GBzr3uIWKyQLMa56PUeJDJ7zgx9zYN56SWoTfFCtJhhs1npk-t0plbcCoKmxjgQkSOXSblAs9OLTAf_lp2hiRqjzwXRGIPj_zCVmJ2iYDjHH3qRM0dsNwCbXB8DEIDxCMnAn3o1qgH-8bFbEbfPYrnJ_OS9sV8NK8UHRKaQgcLFeIu1zP0masJhaoEGXmCCejoQTz6C-Y0bulLAksZw1eFCDt0-QSsmv-EM2aEcI9UIzCwZWAOG2mWxuK_e6udtnfPvj-b-sB6Ww3mWFV6xLj3zO66E9yQjz46uM3V4yzbxXduHlup6QnEZHgfFRPKCVtcr2zSk-I0vqMCSGvoscB_mkHo6nnohBNy9c5nK05AdZQgH3Z4IwoXCD1vUXp8PrJQtVH5z8pZKdex3uS7HIyy3KrHt59-C1vs0aJOPiH6HyH5bWntJKa3dJM6Yo6Le8pSbj_fV_o5imCOr5oGoj0FMqeYqJKatsCptnet2csaEuZ8Zx4crk1PJzQfPwZhk1lxgRa-lyIQmWBKLKIBsXWSTx0KhUt1ECXU1INNiIc6Lxgn9-SH82ElEmnZ4GTfxpRfDeO65emevWm7BW5lCafiItr4YJX_6Knv8UmtDwk%3D',
  'YOUTH_WITHDRAWBODY': '',
  'YOUTH_SHAREBODY': 'access=WIFI&app_version=2.0.2&channel=80000000&channel_code=80000000&cid=80000000&client_version=2.0.2&device_brand=iphone&device_id=50064191&device_model=iPhone&device_platform=iphone&device_type=iphone&isnew=1&mobile_type=2&net_type=1&openudid=848fd169d2c54f95d562bdd9968d197e&os_version=14.1&phone_code=848fd169d2c54f95d562bdd9968d197e&phone_network=WIFI&platform=3&request_time=1623562319&resolution=828x1792&sm_device_id=20210128174048a433e0d65b118d07ac8d99a1e0d03fa6017273224847e73f&szlm_ddid=D2OCIF12y7rYwoxdWj%2BWA0khkgkIGBwNuzECXmh7wlq7AX00&time=1623562319&token=e87f38763ecc7c9975ae111d5491ecd5&uid=53327873&uuid=848fd169d2c54f95d562bdd9968d197e'
}
cookies2 = {
  'YOUTH_HEADER': {"Accept-Encoding":"gzip, deflate, br","Cookie":"sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2254100793%22%2C%22%24device_id%22%3A%2217866e0ae19917-0992f5a93eb2c1-754c1651-370944-17866e0ae1ae85%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2217866e0ae19917-0992f5a93eb2c1-754c1651-370944-17866e0ae1ae85%22%7D; Hm_lpvt_268f0a31fc0d047e5253dd69ad3a4775=1616633695; Hm_lvt_268f0a31fc0d047e5253dd69ad3a4775=1616633620,1616633633,1616633687,1616633695; Hm_lpvt_6c30047a5b80400b0fd3f410638b8f0c=1616633695; Hm_lvt_6c30047a5b80400b0fd3f410638b8f0c=1616602413,1616632007,1616632253,1616633695; sensorsdata2019jssdkcross=%7B%22distinct_id%22%3A%2254100793%22%2C%22%24device_id%22%3A%2217866c7aae8538-04a4df6a074686-754c1651-370944-17866c7aae9c82%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2217866c7aae8538-04a4df6a074686-754c1651-370944-17866c7aae9c82%22%7D; sajssdk_2019_cross_new_user=1","Connection":"keep-alive","Content-Type":"","Accept":"*/*","Host":"kd.youth.cn","User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148","Referer":"https://kd.youth.cn/h5/20190301taskcenter/ios/index.html?uuid=848fd169d2c54f95d562bdd9968d197e&sign=76ed0a2278dd5133db1dc49ec2436869&channel_code=80000000&uid=54100793&channel=80000000&access=WIfI&app_version=1.8.2&device_platform=iphone&cookie_id=0391fe5841a740f7dc16321428cf3ad3&openudid=848fd169d2c54f95d562bdd9968d197e&device_type=1&device_brand=iphone&sm_device_id=20210128174048a433e0d65b118d07ac8d99a1e0d03fa6017273224847e73f&device_id=50064191&version_code=182&os_version=14.1&cookie=MDAwMDAwMDAwMJCMpN-w09Wtg5-Bb36eh6CPqHualq2jmrCarWOxp3mwhHyYm67eqmqXr6NthJl7mI-shMmXeqDau4StacS3o7GFonqYr8-uq4GJl2uEY2Ft&device_model=iPhone_6_Plus&subv=1.5.1&&cookie=MDAwMDAwMDAwMJCMpN-w09Wtg5-Bb36eh6CPqHualq2jmrCarWOxp3mwhHyYm67eqmqXr6NthJl7mI-shMmXeqDau4StacS3o7GFonqYr8-uq4GJl2uEY2Ft&cookie_id=0391fe5841a740f7dc16321428cf3ad3","Accept-Language":"zh-cn","X-Requested-With":"XMLHttpRequest"},
  'YOUTH_READBODY': 'p=9NwGV8Ov71o%3DgW5NEpb6rjb84bkaCQyOq-myT0C-Ktb_kF97hamPuz4ZZk3rmRrVU_m2Z51XN3szZYaCPxNG07BYjyjwYkBVGTfTGYPVecze9u-jGHCQmfvey4yZrPyKR-cA01PbV3h61GBiHFc-skGrpoDK0eliCfJPX7f9_IVT-MEKcW_xpZC9uwvN42PDuOW5dbj3maVjeVWpPiN8uQFvzpmRAGq-FlitLubMZVYWQzbdLFoJwi2LVYVKBLzT6yOCaquZNgiqWuhUyu1eid4RHrIdPqF8REz_CDJhm2BXnCVIaPJy2e-mrroajqGtcifr_xg8Iw3ORT_Nx_kpDC1Hv6H8xZxetaY68mMN1bNRwVIOY-jc5TruvgoyZlEgiefHew1gif1DBhyEuSBuseEnvv08Rxb7Jk1lG92XjYo20J7xPFD1BxSG-FrVoUGWUQYX7Z3awPdWZjAAk2dSlOVIf67-9g3aqxKsXpZH2G39asOkWxleUtCPxaFUmb6tAHGAuy4rUlMEEqUx-V48Zv9xMw6_Rp2tWGlIsXnS9wFw1-rLF2sNQZd4cYhTsEl_mhtyaTJWN9lycIApCUhX93wHPN394z8RntvxP9NrprrW3wRW9m1oWSm3_0zgD-Csu8Ca4NBxif-DXKIkemiJdMrMumVY3ljJEEAL2uZ3mfZklLjAy9mxGDfAFwIaSQQsWKHy2B79DT2aXWTP4QK1CJFG92VcpmGbBf6OmMYQ1qHROWLntmlR2JhTJO5tc8Z_cO36hih7DmQvYWoNdFf4vPWcVl7fa7bGx7yTtUBmaNztUKk8VyvGcUMcmQSIt938kOm11J0U067AFE5UtEnP0c1fKJqgTn1qpQ%3D%3D',
  'YOUTH_REDBODY': 'p=9NwGV8Ov71o%3DgW5NEpb6rjab0hHSxXenkWHSkCwB26b061WrSAMkZbAILHOoAyhQG5tUdJ3zAgkHKSBdPxl-sr3HPko2gWDheswwTVXLXLavpKzrPq37YjTB-uFCG2XpdG1CoLnhEzrwJcKDqm1XuUwmh_TSAzsW1sQnL-wgW0cVAkfVDq0sdh9GWbJoWgXjPOVC1iOJBpxOhX5ZG39vUSIfORfrmlEbhtdMmtl7j-4Cflkn0vE67ZNqA44aB2dlASletUj2cOXA28m06TasM1R3QZtLxLkmgeLWM86o14Xmc8mX9rHZkZ4sw7YRx1XSvlQeuiTWp2jzYh5S8bWGGTaHhB2KfdHuoJrt6dQLOcj9KI4TSkdF9Vcdbv6l9DeLOsVhzBAP_RRRIPSomoFbI_cu_4QjAfuXdpKe0nLcXomtT_AiUHvIJImy3eb87j16YwWonlOKPNYdMaXGtYxp2YG9zJXUsF-P5T6y32_WhsgHGCmS18EFrNpASntLt3sDvpivH_wO5CmzswWTZeJrk9_wXRQFTl-7S-TXxbGXoyE_Ukm5D-xhKmjkdaFm_5zZhSudAb6iurzfFb56IjgDwX4FLrwkyTrbjb4gdekVvFIyfPfJB6QfE2XVKwCGZ1Z4D8JbCdv27GQ8o4hysxxl9j2RJb44uUXjUssTSWUV-uLoMNK8xQQxLMN6KA1A5wA8cX5e15i37PCmF_UpyDhHLwZ-_x2LxMjRY1TKPx-y8-91nKo-na9RbQtZThVAtFDeUgf5-oD5HYQa_e47aCHGv27Cp85nHt5WxO8aHB86xRWN1Yzeyib3QNc-9v7pCQIiymwxJ7CO5Dq2XNhZqYXyLpO0y34tpVtUzW1Ea0BMkTjfQ0125oTvb9k%3D',  
  'YOUTH_READTIMEBODY': 'p=9NwGV8Ov71o%3DgW5NEpb6rjb84bkaCQyOq-myT0C-Ktb_kF97hamPuz4ZZk3rmRrVU_m2Z51XN3szZYaCPxNG07BYjyjwYkBVGTfTGYPVecze9u-jGHCQmfvey4yZrPyKR-cA01PbV3h61GBiHFc-skGrpoDK0eliCfJPX7f9_IVT-MEKcW_xpZC9uwvN42PDuOW5dbj3maVjeVWpPiN8uQFvzpmRAGq-FlitLubMZVYWQzbdLFoJwi2LVYVKBLzT6yOCaquZNgiqWuhUyu1eid4RrzeWcO1n5qfgnUWDlBeGYRe7Pl6PXyUBCVvB5OVcFuI8VCurLYS8PUJ-fwchbyf_5KDYrsK1-1zuFgu1lgeTWcYJ3AHyPy-pfklgYif_JyC9nYSL6KFe5kFVyvUTgY1C-A0-galqu5xpWD_4SZ8LgE6P75QgHM7YxGPKucATSz-9iVJ6R73pLApbTCRTznq4SZTn0acuKEOZ3VNVo7x7YGAE2PB92LDrKl0rZTe9wqFyGwhLqN8fyvLzAIrsg2l-tWrfi4OXwkRjAYIKE00hxXWR6iF7Q0l5BSLdCBtDk12HZs_8qnKGUrMHGJCQ5Yt9BTlMNtRXMv-7wdDjGN4uxn0c5JRhycg6NFzxVXbUkcKzK8U6CxHgSsqJ5v3Qwxum8pYLXuF4-PQo4ghbd_IF1RYu9USg4lWOI_CsZMJyLiC6TvcMj2g6bcJm0yfa7M94eOfXzZTxDxamzm25RWq7RR0jxBfqBbczEy7St7cso1_CPSAB9Woh4igflac4XpOkNg2fSdAvi7M0nC_rs9TVIIBBJdy6lH_jstEOV20DHM57nXX8SLr39BCveFBv-6g%3D',
  'YOUTH_WITHDRAWBODY': '',
  'YOUTH_SHAREBODY': 'access=WIFI&app_version=2.0.2&channel=80000000&channel_code=80000000&cid=80000000&client_version=2.0.2&device_brand=iphone&device_id=50064191&device_model=iPhone&device_platform=iphone&device_type=iphone&isnew=1&mobile_type=2&net_type=1&openudid=848fd169d2c54f95d562bdd9968d197e&os_version=14.1&phone_code=848fd169d2c54f95d562bdd9968d197e&phone_network=WIFI&platform=3&request_time=1623650356&resolution=828x1792&sm_device_id=20210128174048a433e0d65b118d07ac8d99a1e0d03fa6017273224847e73f&szlm_ddid=D2OCIF12y7rYwoxdWj%2BWA0khkgkIGBwNuzECXmh7wlq7AX00&time=1623650356&token=81c617856211474f0a1457b8559f0124&uid=54100793&uuid=848fd169d2c54f95d562bdd9968d197e'
}
COOKIELIST = [cookies1,cookies2]  # 多账号准备

# ac读取环境变量
if "YOUTH_HEADER1" in os.environ:
  COOKIELIST = []
  for i in range(5):
    headerVar = f'YOUTH_HEADER{str(i+1)}'
    readBodyVar = f'YOUTH_READBODY{str(i+1)}'
    redBodyVar = f'YOUTH_REDBODY{str(i+1)}'
    readTimeBodyVar = f'YOUTH_READTIMEBODY{str(i+1)}'
    withdrawBodyVar = f'YOUTH_WITHDRAWBODY{str(i+1)}'
    shareBodyVar = f'YOUTH_SHAREBODY{str(i+1)}'
    if headerVar in os.environ and os.environ[headerVar] and readBodyVar in os.environ and os.environ[readBodyVar] and redBodyVar in os.environ and os.environ[redBodyVar] and readTimeBodyVar in os.environ and os.environ[readTimeBodyVar]:
      globals()['cookies'+str(i + 1)]["YOUTH_HEADER"] = json.loads(os.environ[headerVar])
      globals()['cookies'+str(i + 1)]["YOUTH_READBODY"] = os.environ[readBodyVar]
      globals()['cookies'+str(i + 1)]["YOUTH_REDBODY"] = os.environ[redBodyVar]
      globals()['cookies' + str(i + 1)]["YOUTH_READTIMEBODY"] = os.environ[readTimeBodyVar]
      globals()['cookies' + str(i + 1)]["YOUTH_WITHDRAWBODY"] = os.environ[withdrawBodyVar]
      globals()['cookies' + str(i + 1)]["YOUTH_SHAREBODY"] = os.environ[shareBodyVar]
      COOKIELIST.append(globals()['cookies'+str(i + 1)])
  print(COOKIELIST)

cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(cur_path)[0]
sys.path.append(root_path)
YOUTH_HOST = "https://kd.youth.cn/WebApi/"

def get_standard_time():
  """
  获取utc时间和北京时间
  :return:
  """
  # <class 'datetime.datetime'>
  utc_datetime = datetime.utcnow().replace(tzinfo=timezone.utc)  # utc时间
  beijing_datetime = utc_datetime.astimezone(timezone(timedelta(hours=8)))  # 北京时间
  return beijing_datetime

def pretty_dict(dict):
    """
    格式化输出 json 或者 dict 格式的变量
    :param dict:
    :return:
    """
    return print(json.dumps(dict, indent=4, ensure_ascii=False))

def sign(headers):
  """
  签到
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = 'https://kd.youth.cn/TaskCenter/sign'
  try:
    response = requests_session().post(url=url, headers=headers, timeout=30).json()
    print('签到')
    print(response)
    if response['status'] == 1:
      return response
    else:
      return
  except:
    print(traceback.format_exc())
    return

def signInfo(headers):
  """
  签到详情
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = 'https://kd.youth.cn/TaskCenter/getSign'
  try:
    response = requests_session().post(url=url, headers=headers, timeout=30).json()
    print('签到详情')
    print(response)
    if response['status'] == 1:
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def punchCard(headers):
  """
  打卡报名
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}PunchCard/signUp'
  try:
    response = requests_session().post(url=url, headers=headers, timeout=30).json()
    print('打卡报名')
    print(response)
    if response['code'] == 1:
      return response
    else:
      return
  except:
    print(traceback.format_exc())
    return

def doCard(headers):
  """
  早起打卡
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}PunchCard/doCard'
  try:
    response = requests_session().post(url=url, headers=headers, timeout=30).json()
    print('早起打卡')
    print(response)
    if response['code'] == 1:
      shareCard(headers=headers)
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def shareCard(headers):
  """
  打卡分享
  :param headers:
  :return:
  """
  time.sleep(0.3)
  startUrl = f'{YOUTH_HOST}PunchCard/shareStart'
  endUrl = f'{YOUTH_HOST}PunchCard/shareEnd'
  try:
    response = requests_session().post(url=startUrl, headers=headers, timeout=30).json()
    print('打卡分享')
    print(response)
    if response['code'] == 1:
      time.sleep(0.3)
      responseEnd = requests_session().post(url=endUrl, headers=headers, timeout=30).json()
      if responseEnd['code'] == 1:
        return responseEnd
    else:
      return
  except:
    print(traceback.format_exc())
    return

def luckDraw(headers):
  """
  打卡分享
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}PunchCard/luckdraw'
  try:
    response = requests_session().post(url=url, headers=headers, timeout=30).json()
    print('七日签到')
    print(response)
    if response['code'] == 1:
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def timePacket(headers):
  """
  计时红包
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}TimePacket/getReward'
  try:
    response = requests_session().post(url=url, data=f'{headers["Referer"].split("?")[1]}', headers=headers, timeout=30).json()
    print('计时红包')
    print(response)
    return
  except:
    print(traceback.format_exc())
    return

def watchWelfareVideo(headers):
  """
  观看福利视频
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}NewTaskIos/recordNum?{headers["Referer"].split("?")[1]}'
  try:
    response = requests_session().get(url=url, headers=headers, timeout=30).json()
    print('观看福利视频')
    print(response)
    return
  except:
    print(traceback.format_exc())
    return

def shareArticle(headers, body):
  """
  分享文章
  :param headers:
  :return:
  """
  url = 'https://ios.baertt.com/v2/article/share/put.json'
  headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('分享文章')
    print(response)
    return
  except:
    print(traceback.format_exc())
    return

def threeShare(headers, action):
  """
  三餐分享
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}ShareNew/execExtractTask'
  headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
  body = f'{headers["Referer"].split("?")[1]}&action={action}'
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('三餐分享')
    print(response)
    return
  except:
    print(traceback.format_exc())
    return

def openBox(headers):
  """
  开启宝箱
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}invite/openHourRed'
  try:
    response = requests_session().post(url=url, headers=headers, timeout=30).json()
    print('开启宝箱')
    print(response)
    if response['code'] == 1:
      share_box_res = shareBox(headers=headers)
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def shareBox(headers):
  """
  宝箱分享
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}invite/shareEnd'
  try:
    response = requests_session().post(url=url, headers=headers, timeout=30).json()
    print('宝箱分享')
    print(response)
    if response['code'] == 1:
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def friendList(headers):
  """
  好友列表
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}ShareSignNew/getFriendActiveList'
  try:
    response = requests_session().get(url=url, headers=headers, timeout=30).json()
    print('好友列表')
    print(response)
    if response['error_code'] == '0':
      if len(response['data']['active_list']) > 0:
        for friend in response['data']['active_list']:
          if friend['button'] == 1:
            time.sleep(1)
            friendSign(headers=headers, uid=friend['uid'])
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def friendSign(headers, uid):
  """
  好友签到
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}ShareSignNew/sendScoreV2?friend_uid={uid}'
  try:
    response = requests_session().get(url=url, headers=headers, timeout=30).json()
    print('好友签到')
    print(response)
    if response['error_code'] == '0':
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def sendTwentyScore(headers, action):
  """
  每日任务
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}NewTaskIos/sendTwentyScore?{headers["Referer"].split("?")[1]}&action={action}'
  try:
    response = requests_session().get(url=url, headers=headers, timeout=30).json()
    print(f'每日任务 {action}')
    print(response)
    if response['status'] == 1:
      return response
    else:
      return
  except:
    print(traceback.format_exc())
    return

def watchAdVideo(headers):
  """
  看广告视频
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = 'https://kd.youth.cn/taskCenter/getAdVideoReward'
  headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
  try:
    response = requests_session().post(url=url, data="type=taskCenter", headers=headers, timeout=30).json()
    print('看广告视频')
    print(response)
    if response['status'] == 1:
      return response
    else:
      return
  except:
    print(traceback.format_exc())
    return

def watchGameVideo(body):
  """
  激励视频
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = 'https://ios.baertt.com/v5/Game/GameVideoReward.json'
  headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
  try:
    response = requests_session().post(url=url, headers=headers, data=body, timeout=30).json()
    print('激励视频')
    print(response)
    if response['success'] == True:
      return response['items']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def visitReward(body):
  """
  回访奖励
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = 'https://ios.baertt.com/v5/mission/msgRed.json'
  headers = {
    'User-Agent': 'KDApp/1.8.0 (iPhone; iOS 14.2; Scale/3.00)',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
  }
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('回访奖励')
    print(response)
    if response['success'] == True:
      return response['items']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def articleRed(body):
  """
  惊喜红包
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = 'https://ios.baertt.com/v5/article/red_packet.json'
  headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
  }
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('惊喜红包')
    print(response)
    if response['success'] == True:
      return response['items']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def readTime(body):
  """
  阅读时长
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = 'https://ios.baertt.com/v5/user/stay.json'
  headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
  }
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('阅读时长')
    print(response)
    if response['error_code'] == '0':
      return response
    else:
      return
  except:
    print(traceback.format_exc())
    return

def rotary(headers, body):
  """
  转盘任务
  :param headers:
  :return:
  """
  time.sleep(0.3)
  currentTime = time.time()
  url = f'{YOUTH_HOST}RotaryTable/turnRotary?_={currentTime}'
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('转盘任务')
    print(response)
    return response
  except:
    print(traceback.format_exc())
    return

def rotaryChestReward(headers, body):
  """
  转盘宝箱
  :param headers:
  :return:
  """
  time.sleep(0.3)
  currentTime = time.time()
  url = f'{YOUTH_HOST}RotaryTable/getData?_={currentTime}'
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('转盘宝箱')
    print(response)
    if response['status'] == 1:
      i = 0
      while (i <= 3):
        chest = response['data']['chestOpen'][i]
        if response['data']['opened'] >= int(chest['times']) and chest['received'] != 1:
          time.sleep(1)
          runRotary(headers=headers, body=f'{body}&num={i+1}')
        i += 1
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def runRotary(headers, body):
  """
  转盘宝箱
  :param headers:
  :return:
  """
  time.sleep(0.3)
  currentTime = time.time()
  url = f'{YOUTH_HOST}RotaryTable/chestReward?_={currentTime}'
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('领取宝箱')
    print(response)
    if response['status'] == 1:
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def doubleRotary(headers, body):
  """
  转盘双倍
  :param headers:
  :return:
  """
  time.sleep(0.3)
  currentTime = time.time()
  url = f'{YOUTH_HOST}RotaryTable/toTurnDouble?_={currentTime}'
  try:
    response = requests_session().post(url=url, data=body, headers=headers, timeout=30).json()
    print('转盘双倍')
    print(response)
    if response['status'] == 1:
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def incomeStat(headers):
  """
  收益统计
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'https://kd.youth.cn/wap/user/balance?{headers["Referer"].split("?")[1]}'
  try:
    response = requests_session().get(url=url, headers=headers, timeout=50).json()
    print('收益统计')
    print(response)
    if response['status'] == 0:
      return response
    else:
      return
  except:
    print(traceback.format_exc())
    return

def withdraw(body):
  """
  自动提现
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = 'https://ios.baertt.com/v5/wechat/withdraw2.json'
  headers = {
    'User-Agent': 'KDApp/1.8.0 (iPhone; iOS 14.2; Scale/3.00)',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
  }
  try:
    response = requests_session().post(url=url, headers=headers, data=body, timeout=30).json()
    print('自动提现')
    print(response)
    if response['success'] == True:
      return response['items']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def bereadRed(headers):
  """
  时段红包
  :param headers:
  :return:
  """
  time.sleep(0.3)
  url = f'{YOUTH_HOST}Task/receiveBereadRed'
  try:
    response = requests_session().post(url=url, headers=headers, timeout=30).json()
    print('时段红包')
    print(response)
    if response['code'] == 1:
      return response['data']
    else:
      return
  except:
    print(traceback.format_exc())
    return

def run():
  title = f'📚中青看点'
  content = ''
  result = ''
  beijing_datetime = get_standard_time()
  print(f'\n【中青看点】{beijing_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
  hour = beijing_datetime.hour
  for i, account in enumerate(COOKIELIST):
    headers = account['YOUTH_HEADER']
    readBody = account['YOUTH_READBODY']
    redBody = account['YOUTH_REDBODY']
    readTimeBody = account['YOUTH_READTIMEBODY']
    withdrawBody = account['YOUTH_WITHDRAWBODY']
    shareBody = account['YOUTH_SHAREBODY']
    rotaryBody = f'{headers["Referer"].split("&")[15]}&{headers["Referer"].split("&")[8]}'
    sign_res = sign(headers=headers)
    if sign_res and sign_res['status'] == 1:
      content += f'【签到结果】：成功 🎉 明日+{sign_res["nextScore"]}青豆'
    elif sign_res and sign_res['status'] == 2:
      send(title=title, content=f'【账户{i+1}】Cookie已过期，请及时重新获取')
      continue

    sign_info = signInfo(headers=headers)
    if sign_info:
      content += f'\n【账号】：{sign_info["user"]["nickname"]}'
      content += f'\n【签到】：+{sign_info["sign_score"]}青豆 已连签{sign_info["total_sign_days"]}天'
      result += f'【账号】: {sign_info["user"]["nickname"]}'
    friendList(headers=headers)
    if hour > 12:
      punch_card_res = punchCard(headers=headers)
      if punch_card_res:
        content += f'\n【打卡报名】：打卡报名{punch_card_res["msg"]} ✅'
    if hour >= 5 and hour <= 8:
      do_card_res = doCard(headers=headers)
      if do_card_res:
        content += f'\n【早起打卡】：{do_card_res["card_time"]} ✅'
    luck_draw_res = luckDraw(headers=headers)
    if luck_draw_res:
      content += f'\n【七日签到】：+{luck_draw_res["score"]}青豆'
    visit_reward_res = visitReward(body=readBody)
    if visit_reward_res:
      content += f'\n【回访奖励】：+{visit_reward_res["score"]}青豆'
    shareArticle(headers=headers, body=shareBody)
    for action in ['beread_extra_reward_one', 'beread_extra_reward_two', 'beread_extra_reward_three']:
      time.sleep(5)
      threeShare(headers=headers, action=action)
    open_box_res = openBox(headers=headers)
    if open_box_res:
      content += f'\n【开启宝箱】：+{open_box_res["score"]}青豆 下次奖励{open_box_res["time"] / 60}分钟'
    watch_ad_video_res = watchAdVideo(headers=headers)
    if watch_ad_video_res:
      content += f'\n【观看视频】：+{watch_ad_video_res["score"]}个青豆'
    watch_game_video_res = watchGameVideo(body=readBody)
    if watch_game_video_res:
      content += f'\n【激励视频】：{watch_game_video_res["score"]}个青豆'
    # article_red_res = articleRed(body=redBody)
    # if article_red_res:
    #   content += f'\n【惊喜红包】：+{article_red_res["score"]}个青豆'
    read_time_res = readTime(body=readTimeBody)
    if read_time_res:
      content += f'\n【阅读时长】：共计{int(read_time_res["time"]) // 60}分钟'
    if (hour >= 6 and hour <= 8) or (hour >= 11 and hour <= 13) or (hour >= 19 and hour <= 21):
      beread_red_res = bereadRed(headers=headers)
      if beread_red_res:
        content += f'\n【时段红包】：+{beread_red_res["score"]}个青豆'
    for i in range(0, 5):
      time.sleep(5)
      rotary_res = rotary(headers=headers, body=rotaryBody)
      if rotary_res:
        if rotary_res['status'] == 0:
          break
        elif rotary_res['status'] == 1:
          content += f'\n【转盘抽奖】：+{rotary_res["data"]["score"]}个青豆 剩余{rotary_res["data"]["remainTurn"]}次'
          if rotary_res['data']['doubleNum'] != 0 and rotary_res['data']['score'] > 0:
            double_rotary_res = doubleRotary(headers=headers, body=rotaryBody)
            if double_rotary_res:
              content += f'\n【转盘双倍】：+{double_rotary_res["score"]}青豆 剩余{double_rotary_res["doubleNum"]}次'

    rotaryChestReward(headers=headers, body=rotaryBody)
    for i in range(5):
      watchWelfareVideo(headers=headers)
    timePacket(headers=headers)
    for action in ['watch_article_reward', 'watch_video_reward', 'read_time_two_minutes', 'read_time_sixty_minutes', 'new_fresh_five_video_reward', 'first_share_article']:
      time.sleep(5)
      sendTwentyScore(headers=headers, action=action)
    stat_res = incomeStat(headers=headers)
    if stat_res['status'] == 0:
      for group in stat_res['history'][0]['group']:
        content += f'\n【{group["name"]}】：+{group["money"]}青豆'
      today_score = int(stat_res["user"]["today_score"])
      score = int(stat_res["user"]["score"])
      total_score = int(stat_res["user"]["total_score"])

      if score >= 300000 and withdrawBody:
        with_draw_res = withdraw(body=withdrawBody)
        if with_draw_res:
          result += f'\n【自动提现】：发起提现30元成功'
          content += f'\n【自动提现】：发起提现30元成功'
          send(title=title, content=f'【账号】: {sign_info["user"]["nickname"]} 发起提现30元成功')

      result += f'\n【今日收益】：+{"{:4.2f}".format(today_score / 10000)}'
      content += f'\n【今日收益】：+{"{:4.2f}".format(today_score / 10000)}'
      result += f'\n【账户剩余】：{"{:4.2f}".format(score / 10000)}'
      content += f'\n【账户剩余】：{"{:4.2f}".format(score / 10000)}'
      result += f'\n【历史收益】：{"{:4.2f}".format(total_score / 10000)}\n\n'
      content += f'\n【历史收益】：{"{:4.2f}".format(total_score / 10000)}\n'

  print(content)

  if True:            
  #if beijing_datetime.hour == 23 and beijing_datetime.minute >= 0 and beijing_datetime.minute < 5:
    send(title=title, content=result)
  elif not beijing_datetime.hour == 23:
    print('未进行消息推送，原因：没到对应的推送时间点\n')
  else:
    print('未在规定的时间范围内\n')

if __name__ == '__main__':
   run()
