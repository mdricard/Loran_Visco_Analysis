import numpy as np
import matplotlib.pyplot as plt
from BiomechTools import low_pass, zero_crossing, max_min, simpson_nonuniform


class Visco:
    n_reps = 0
    energy_absorbed = np.zeros(20)
    energy_returned = np.zeros(20)
    peak_torque = np.zeros(20)
    stiffness = np.zeros(20)

    def __init__(self, fn):
        with open(fn) as infile:
            temp = infile.readline()
            temp = infile.readline()
            header = temp.split(',')
            self.n = int(header[7]) - 2
            self.sampling_rate = int(header[8])
            self.mass = float(header[9])
            self.ht = float(header[10])
            self.limblen = float(header[11])
            self.attachmentlen = float(header[12])
            self.gender = header[13]
        data = np.genfromtxt(fn, delimiter=',', skip_header=2)
        self.pt = data[:, 0]
        self.tor = data[:, 1]
        self.pos = data[:, 2]
        self.vel = data[:, 3]
        self.MHemg = data[:, 4]
        self.VLemg = data[:, 5]
        self.mmg = data[:, 6]

        self.smooth_tor = []
        self.smooth_pos = []
        self.smooth_vel = []
        self.rep_start = np.zeros(20, dtype=np.int32)
        self.max_loc = np.zeros(20, dtype=np.int32)
        self.rep_end = np.zeros(20, dtype=np.int32)

    def plot_all(self):
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(self.pt, self.tor)
        ax2.plot(self.pt, self.pos)
        plt.show()


    def filter_data(self):
        self.smooth_tor = low_pass(self.tor, self.sampling_rate, 4)
        self.smooth_pos = low_pass(self.pos, self.sampling_rate, 4)

    def get_min(self, first_pt, last_pt):
        min_location = first_pt
        min_val = self.smooth_pos[first_pt]
        for i in range(first_pt, last_pt):
            if self.smooth_pos[i] < min_val:
                min_location = i
                min_val = self.smooth_pos[i]
        return min_location

    def get_max(self, first_pt, last_pt):
        max_location = first_pt
        max_val = self.smooth_pos[first_pt]
        for i in range(first_pt, last_pt):
            if self.smooth_pos[i] > max_val:
                max_location = i
                max_val = self.smooth_pos[i]
        return max_location

    def find_rep(self, show_graph):
        p_18, r_or_f = zero_crossing(self.smooth_pos, 135, 10, self.n - 2)
        if r_or_f[0] == 'falling':      # make sure first point is falling as it pos passes reference (135 deg)
            start_pt = 0
            cnt = len(p_18)
        else:
            start_pt = 1
            cnt = len(p_18) - 1
        rep = 0
        cntr = start_pt       # cntr is used to check for another rep after exiting for loop
        #print(p_18)
        #print('count: ', cnt)
        for i in range(start_pt, cnt-3, 2):
            self.rep_start[rep] = self.get_min(p_18[i], p_18[i + 1])
            self.max_loc[rep] = self.get_max(p_18[i + 1], p_18[i + 2])
            self.rep_end[rep] = self.get_min(p_18[i + 2], p_18[i + 3])
            cntr = cntr + 2
            rep = rep + 1
        # now use cntr to check for one last rep
        if cntr <= (len(p_18) - 2):
            self.rep_start[rep] = self.rep_end[rep - 1]
            self.max_loc[rep] = self.get_max(p_18[cntr + 1], p_18[cntr + 2])
            self.rep_end[rep] = self.get_min(p_18[cntr + 2], p_18[cntr + 3])
            rep = rep + 1
        self.n_reps = rep
        if show_graph:
            plt.plot(self.pt, self.smooth_pos)
            for rep in range(self.n_reps):
                plt.vlines(self.rep_start[rep], 100, 180, linestyles='solid', colors='green')
                plt.vlines(self.max_loc[rep], 100, 180, linestyles='dashed', colors='red')
                plt.vlines(self.rep_end[rep], 100, 180, linestyles='dotted', colors='black')
            for i in range(len(p_18)):
                plt.scatter(p_18[i], self.smooth_pos[p_18[i]])
            plt.show()

    def analyze_reps(self):
        for rep in range(self.n_reps):
            load_area = simpson_nonuniform(self.smooth_pos[self.rep_start[rep] : self.max_loc[rep]], self.smooth_tor[self.rep_start[rep] : self.max_loc[rep]])
            self.energy_returned[rep] = -1.0 * simpson_nonuniform(self.smooth_pos[self.max_loc[rep] : self.rep_end[rep]], self.smooth_tor[self.max_loc[rep] : self.rep_end[rep]])
            self.energy_absorbed[rep] = load_area - self.energy_returned[rep]
            self.peak_torque[rep] = self.smooth_tor[self.max_loc[rep]]
            self.stiffness[rep] = (self.smooth_tor[self.max_loc[rep]] - self.smooth_tor[self.rep_start[rep]]) / (
                np.radians(self.smooth_pos[self.max_loc[rep]] - self.smooth_pos[self.rep_start[rep]]))


    def graph_rep(self, rep):
        x = self.smooth_pos[self.rep_start[rep] : self.rep_end[rep]]
        y = self.smooth_tor[self.rep_start[rep] : self.rep_end[rep]]
        plt.plot(x, y)
        plt.scatter(x[0], y[0])     # identify the start of the repetition
        plt.show()

    def graph_all_reps(self):
        for rep in range(self.n_reps):
            x = self.smooth_pos[self.rep_start[rep] : self.rep_end[rep]]
            y = self.smooth_tor[self.rep_start[rep] : self.rep_end[rep]]
            plt.plot(x, y)
        plt.show()

    def print_results(self):
        for rep in range(self.n_reps):
            print('Peak Torque (Nm): ' + format(self.peak_torque[rep], '.2f'))
            print('Stiffness (Nm/rad): ' + format(self.stiffness[rep], '.2f'))
            print('Energy Absorbed (Nm): ' + format(self.energy_absorbed[rep], '.2f'))
            print('Energy Returned (Nm): ' + format(self.energy_returned[rep], '.2f'))