def init_system_visualization(n_atoms, global_radius, local_radius, gradients, Alpha_gr, Alpha_qf, Gamma_qf,
                              GaussianSigma_first, GaussianSigma, grid_step):
    infolist = []
    print("############# INITIAL VALUES ###############")
    print("")
    infolist.append(f"Number of Atoms (Dimensions of the Simulation): {n_atoms}")
    infolist.append(f"Global Radius (Changes range in every dimension): {global_radius}")
    infolist.append(f"Local Radius: {local_radius}")
    infolist.append(f"Gradients: {gradients}")
    infolist.append(f"Alpha for Gradients: {Alpha_gr}")
    infolist.append(f"Alpha for Q-Function: {Alpha_qf}")
    infolist.append(f"Gamma for Q-Function: {Gamma_qf}")
    infolist.append(f"Gassian Sigma for first Iteration: {GaussianSigma_first}")
    infolist.append(f"Gassian Sigma for next Iterations: {GaussianSigma}")
    infolist.append(f"Grid step size: {grid_step}")
    for i in infolist:
        print(i)
    print("")
    print("#############################################")
    file_name = "info.txt"
    with open(file_name, "w") as file:
        # Write each string in a new line
        for string in infolist:
            file.write(string + "\n")


def runtime_visualizarion(id, info_dic, act_type, actions, data, reward,it_path):
    info_dic["actiontype"].append(act_type)
    info_dic["actionvalues"].append(actions)
    info_dic["locations"].append(data[7])
    info_dic["l_weights"].append(data[6])
    info_dic["u_weights"].append(data[5])
    info_dic["deltas"].append(data[4])
    info_dic["diffs"].append(data[3])
    info_dic["nextQvalues"].append(data[2])
    info_dic["cur_qvals"].append(data[1])
    info_dic["rewards"].append(reward)
    infolist = []
    print(f"######## {id} ITERATION RESULT ########")
    print("                                        ")
    infolist.append(f"Next action suggested by QF: {data[8]}")  # data[8] = next_action
    for idx, loc in enumerate(info_dic["locations"]):
        infolist.append(
            f"loc: {str(loc)} - act: {info_dic['actionvalues'][idx]} - rew: {round(info_dic['rewards'][idx], 2)} - Delta: {info_dic['deltas'][idx]} - Diff: {info_dic['diffs'][idx]} - n-qval: {info_dic['nextQvalues'][idx]} - o-qval: {info_dic['cur_qvals'][idx]} - uW: {info_dic['u_weights'][idx]} - lW: {info_dic['l_weights'][idx]} - Act: {info_dic['actiontype'][idx]}")

    for i in infolist:
        print(i)
    print("                                        ")
    print("#############################################")
    file_name = it_path + "/info.txt"
    with open(file_name, "w") as file:
        for string in infolist:
            file.write(string + "\n")