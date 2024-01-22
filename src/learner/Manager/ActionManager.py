import random

from src.simlator.dispatcher import *
from master_db.DataInventory import *
class ActionManager:
    action_type = ""
    dispatcher = Dispatcher()
    setup_type_list = []
    action_count = ""
    action_dimension = []

    @classmethod
    def get_lot(cls, candidate_list, action, current_time, eps = None):
        rule_name =None
        if cls.action_type == "dsp_rule":
            rule_name = cls.action_dimension[action]
            candidate_list = cls.dispatcher.dispatching_rule_decision(candidate_list, rule_name, current_time)
            candidate = candidate_list[0]

        elif cls.action_type == "setup":
            setup = cls.action_dimension[action]
            candidate = cls.get_lot_by_setup(candidate_list, setup, current_time)

        elif cls.action_type =="action_masking":
            candidate, action, setup = cls.get_lot_by_action_masking(candidate_list, action,eps)
            return candidate, action, setup

        return rule_name , candidate

    @classmethod
    def set_action_type(cls, action_type, action_list):
        if action_type == "dsp_rule":
            cls.action_type = action_type
            cls.action_count = len(action_list)
            cls.action_dimension = [rule for rule in Parameters.DSP_rule_check.keys() if rule in action_list]
        elif action_type == "setup" or action_type == "action_masking":
            cls.action_type = action_type
            cls.action_dimension = [job.jobType for job in DataInventory.master_data["Job_db"]]
            cls.action_count = len(cls.action_dimension)

        Parameters.r_param["output_layer"] = cls.action_count
    @classmethod
    def get_lot_by_setup(cls,candidate_list, setup, current_time):

        candidate_list.sort(key=lambda x: x[1] + x[2], reverse=False)

        for candidate in candidate_list:
            if candidate[0].job_type == setup:
                return candidate

        return None

    @classmethod
    def get_lot_by_action_masking(cls, candidate_list, action_list, eps):

        candidate_list.sort(key=lambda x: x[1]+x[2] / x[0].remain_operation, reverse=False)

        candidate_to_setup_list = [candidate[0].job_type for candidate in candidate_list] #setup list

        setup_index = [action for action, setup in enumerate(cls.action_dimension) if setup in candidate_to_setup_list]

        if eps == None :
            _, action, setup = max([action_list[i], i, cls.action_dimension[i]] for i in setup_index)
        else:
            candidate_action_list = []
            for i in setup_index:
                candidate_action_list.append([action_list[i], i, cls.action_dimension[i]])
            candidate_action = random.choice(candidate_action_list)
            _, action, setup = candidate_action

        for candidate in candidate_list:
            if candidate[0].job_type == setup:
                return candidate , action, setup
