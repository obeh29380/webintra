
# 定数定義（グローバル）
STATUS_OPEN_NOTIFIED_WS = 4


def check_input(io_input_9400, ws_9400_input, key_num, ):

    if ws_9400_input[key_num] == STATUS_OPEN_NOTIFIED_WS:
        if io_input_9400 == 2:
            ret_ws_9400_input = 4
            ret_mail_flg_9400 = 0

        elif io_input_9400 == 1:
            ret_ws_9400_input = 1
            ret_mail_flg_9400 = 1 

    if ws_9400_input[key_num] == 3:
        if io_input_9400 == 2:
            ret_ws_9400_input = 2
            ret_mail_flg_9400 = 0

        elif io_input_9400 == 1:
            ret_ws_9400_input = 3
            ret_mail_flg_9400 = 0
    
    return ret_ws_9400_input, ret_mail_flg_9400


ws_9400_input = list()
mail_flg_9400 = list()

# 呼ぶ側
# ch1
ret_ws_9400_input, ret_mail_flg_9400 = check_input(float(io_input[57:58]), ws_9400_input, 1)
ws_9400_input[0] = ret_ws_9400_input
mail_flg_9400[0] = ret_mail_flg_9400

# ch2
ret_ws_9400_input, ret_mail_flg_9400 = check_input(float(io_input[60:62]), ws_9400_input, 2)
ws_9400_input[1] = ret_ws_9400_input
mail_flg_9400[1] = ret_mail_flg_9400