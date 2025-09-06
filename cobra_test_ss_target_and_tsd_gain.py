import cobra_ops

cobra = cobra_ops.cobra_demo()

cobra.ip_set("192.168.2.38")
cobra.change_tsd_gain_1(11, 1)
cobra.change_ss_target_50(11)