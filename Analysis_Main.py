from Visco import *


if __name__ == '__main__':
    file_name = 'd:/Loran Stiffness/S0 C0 80% T1.csv'
    p1 = Visco(file_name)
    #p1.plot_all()
    p1.filter_data()
    p1.find_rep(False)  # change to True to view start, peak torque, end for each rep
    p1.analyze_reps()

    #p1.graph_rep(2)
    p1.print_results()
    p1.graph_all_reps()
