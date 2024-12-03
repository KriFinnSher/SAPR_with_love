from abc import ABC, abstractmethod


class SubApp(ABC):
    def __init__(self, section_type):

        if section_type != "nodes":
            self.input_data = []
        self.entries = []
        self.section_type = section_type

    @abstractmethod
    def init_section(self, base_frame):
        pass

    @abstractmethod
    def create_row(self):
        pass

    @abstractmethod
    def create_row_at_index(self, index, *values):
        pass

    def add_row(self, row_frame):
        index = self.get_row_index(row_frame)
        self.create_row_at_index(index + 1)

    def delete_row(self, row_frame):
        if len(self.entries) == 1:
            return

        index = self.get_row_index(row_frame)
        if self.section_type != "nodes":
            self.input_data.pop(index)
        self.entries[index][0].grid_forget()
        self.entries.pop(index)
        self.refresh_section()

    def fill_section(self, data, name):
        if name == "nodes":
            for idx, node in enumerate(data["nodes"][1:], start=1):
                self.create_row_at_index(idx, node)
        else:
            for idx, instance in enumerate(data[name]):
                match name:
                    case "bars":
                        self.create_row_at_index(idx + 1, instance["first_node"], instance["second_node"],
                                                 instance["a"], instance["e"], instance["max_load"])
                    case "conc_loads":
                        self.create_row_at_index(idx+1, instance["node_num"], instance["conc_load"])
                    case "dist_loads":
                        self.create_row_at_index(idx + 1, instance["bar_num"], instance["dist_load"])



    @abstractmethod
    def refresh_section(self):
        pass

    def get_row_index(self, row_frame):
        if self.section_type == "bars" or "nodes":
            for idx, (frame, label) in enumerate(self.entries):
                if frame == row_frame:
                    return idx
        else:
            for idx, frame in enumerate(self.entries):
                if frame == row_frame:
                    return idx
        return -1

    @abstractmethod
    def get_row_values(self, data):
        pass

    def reset_values(self):
        for frame, label in self.entries:
            frame.grid_forget()
        self.entries.clear()
        self.refresh_section()

        if self.section_type == "nodes":
            self.create_row()
        else:
            self.input_data.clear()