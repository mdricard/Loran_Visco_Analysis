from Visco import *


if __name__ == '__main__':
    file_name = 'D:/Loran Stiffness/S3 C0 100%  T2.csv'
    p1 = Visco(file_name)
    p1.graph_residual()
    #p1.plot_all()
    #p1.filter_data()
    #p1.find_rep(False)  # change to True to view start, peak torque, end for each rep
    #p1.analyze_reps()

    #p1.graph_rep(5)
    #p1.save_rep(5, 'F:/Loran Stiffness/end cushion/S3 C0 100%  T2.csv')
    #p1.print_results()
    #p1.graph_all_reps()
