import plotly.express as px
import pandas as pd
import json
from sqlalchemy import create_engine
from src.common.Parameters import *
import random
from src.learner.common.Hyperparameters import *

class GanttChart:
    gantt_on = Parameters.gantt_on
    gantt_history = pd.DataFrame([], columns=['Type', 'JOB_ID', 'Task', 'Start', 'Finish', 'Resource', 'Rule', 'Step',
                                              'Q_diff', 'Traj'])
    step = 0
    color_by_color_mapper = {'j01': '#FFDDEE', 'j02': '#EEDDFF',
                             'j03': '#FFFFDD', 'j04': '#DDF9FF',
                             'j05': '#B8F5CC'}
    dataset_id = ""

    host = Parameters.db_setting["host"]
    port = Parameters.db_setting["port"]
    user = Parameters.db_setting["user"]
    passwd = Parameters.db_setting["passwd"]
    db = Parameters.db_setting["db"]
    charset = Parameters.db_setting["charset"]

    # SQLAlchemy 연결 엔진 생성
    db_url = f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset={charset}"
    engine = create_engine(db_url)

    text_label = 0

    @classmethod
    def reset(cls):
        cls.gantt_history = pd.DataFrame([],
                                         columns=['Type', 'JOB_ID', 'Task', 'Start', 'Finish', 'Resource', 'Rule',
                                                  'Step',
                                                  'Q_diff', 'Traj'])
        cls.step = 0

    @classmethod
    def save_histories(cls, event_type, job_id, jop, start, end, machine_id, rule, step, q_time_diff, traj):
        cls.gantt_history.loc[cls.step] = dict(
            Type=event_type,
            JOB_ID=job_id,
            Task=jop,
            Start=start,
            Finish=end,
            Resource=machine_id,
            Rule=rule,
            Step=step,
            Q_diff=q_time_diff,
            Traj=traj
        )  # 간트차트를 위한 딕셔너리 생성, 데이터프레임에 집어넣음

        cls.step += 1

    @classmethod
    def update_df(cls):
        step_rule = []
        for i in range(len(cls.gantt_history)):
            if str(cls.gantt_history["Rule"].loc[i]) != "None":
                step_rule.append(str(cls.gantt_history["Step"].loc[i]) + "-" + str(cls.gantt_history["Rule"].loc[i]))
            else:
                step_rule.append("NONE")
        cls.gantt_history["Step-Rule"] = step_rule

        id_op = []
        for i in range(len(cls.gantt_history)):
            if str(cls.gantt_history["Task"].loc[i]) != "None":
                id_op.append(str(cls.gantt_history["JOB_ID"].loc[i]) + "-" + str(cls.gantt_history["Task"].loc[i]))
            else:
                id_op.append("NONE")
        cls.gantt_history["ID_OP"] = id_op

    @classmethod
    def play_gantt(cls, datasetId):
        cls.update_df()
        cls.dataset_id = datasetId
        for i in cls.gantt_on:
            if cls.gantt_on[i]:
                if i == "main_gantt":
                    cls.main_gantt()
                elif i == "machine_on_job_number":
                    cls.mahicne_on_job_number()
                elif i == "machine_gantt":
                    cls.machine_gantt()
                elif i == "DSP_gantt":
                    cls.DSP_gantt()
                elif i == "step_DSP_gantt":
                    cls.step_DSP_gantt()
                elif i == "heatMap_gantt":
                    cls.heatMap_gantt()
                elif i == "job_gantt_for_Q_time":
                    cls.job_gantt_for_Q_time()

    @classmethod
    def save_gantt(cls, datasetId):
        cls.update_df()
        cls.dataset_id = datasetId
        for i in cls.gantt_on:
            if cls.gantt_on[i]:
                # cls.save_reward_learning_data()
                cls.save_reward_learning_data_ver_pbrl()

    @classmethod
    def mahicne_on_job_number(cls):
        fig = px.bar(cls.gantt_history, x="Resource", y="Type", color="Type", facet_row="Type")
        fig.update_yaxes(matches=None)
        fig.show()

    @classmethod
    def machine_gantt(cls):

        # fig,write_html(f"{PathInfo.xlsx}{os.sep}temp_target.html", default_width=2300, default_height=900)
        plotlydf3 = cls.gantt_history.sort_values(by=['Type'], ascending=True)
        fig2 = px.timeline(plotlydf3, x_start="Start", x_end="Finish", y="Type", template="seaborn", color="Resource",
                           text="Resource", width=2000, height=1000)
        fig2.update_traces(marker=dict(line_color="yellow", cmid=1000))
        fig2.show()

    @classmethod
    def DSP_gantt(cls):

        fig3 = px.timeline(cls.gantt_history, x_start="Start", x_end="Finish", y="Resource", template="simple_white",
                           color="Type",
                           color_discrete_sequence=px.colors.qualitative.Dark24, text="Rule", width=2000, height=800)
        [(cls.modify_width(bar, 0.7), cls.modify_text(bar)) for bar in fig3.data if ('setup' in bar.legendgroup)]
        fig3.show()

    @classmethod
    def step_DSP_gantt(cls):
        cls.gantt_history = cls.gantt_history.sort_values(by='Resource')
        y_category_order = cls.gantt_history['Resource'].unique().tolist()

        fig4 = px.timeline(cls.gantt_history, x_start="Start", x_end="Finish", y="Resource", template="simple_white",
                           color="Type",
                           color_discrete_sequence=px.colors.qualitative.Dark24, text="Step-Rule", width=2000,
                           height=800,
                           category_orders={"Resource": y_category_order})
        if cls.color_by_color_mapper:
            for color_mapper, color in cls.color_by_color_mapper.items():
                [cls.modify_bar(bar, color=color) for bar in fig4.data if bar.name == color_mapper]
        # [(cls.modify_width(bar, 0.7), cls.modify_text(bar))
        # for bar in fig4.data if ('setup' in bar.legendgroup)]
        fig4.show()

    @classmethod
    def modify_bar(cls, bar, color=None):
        """
        Bar 속성 지정 메서드
         - color: Bar의 색상
         - opacity: Bar의 투명도 (0 ~ 1)
         - line_width: Bar 테두리 굵기 (0 ~ 1.6)
        """
        if color:
            cls.modify_color(bar, color)

    @classmethod
    def modify_color(cls, bar, color):
        """
        Bar의 색상을 지정할 수 있다.
        """
        bar.marker['color'] = color

    @classmethod
    def heatMap_gantt(cls):

        fig5 = px.timeline(cls.gantt_history, x_start="Start", x_end="Finish", y="Rule", template="simple_white",
                           color="Rule",
                           color_discrete_sequence=px.colors.qualitative.Dark24, text="Step-Rule", width=2000,
                           height=800)
        fig5.show()

    @classmethod
    def main_gantt(cls):
        cls.gantt_history = cls.gantt_history.sort_values(by='Resource')
        cls.gantt_history = cls.to_bottom_setup_df(cls.gantt_history)
        fig6 = px.timeline(cls.gantt_history, x_start="Start", x_end="Finish", y="Resource", template="simple_white",
                           color="Type",
                           color_discrete_sequence=px.colors.qualitative.Dark24, width=2000, height=800)
        [(cls.modify_width(bar, 0.7), cls.modify_text(bar))
         for bar in fig6.data if ('setup' in bar.legendgroup)]
        fig6.show()
        fig6.write_html(
            f"{pathConfig.simulator_result_path}{os.sep}{Parameters.simulation_time}_{cls.dataset_id}_gantt.html")

    @classmethod
    def save_reward_learning_data(cls):
        cls.gantt_history = cls.gantt_history.sort_values(by='Resource')
        cls.gantt_history = cls.to_bottom_setup_df(cls.gantt_history)

        cls.gantt_history.to_csv(f"{pathConfig.reward_learning_data_path}_{cls.dataset_id}_gantt.csv",
                                 index=True)

    @classmethod
    def save_reward_learning_data_ver_pbrl(cls):
        cls.gantt_history_ver_pbrl = cls.gantt_history.sort_values(by='Resource')
        cls.gantt_history_ver_pbrl = cls.to_bottom_setup_df(cls.gantt_history)

        cls.gantt_history_ver_pbrl.to_csv(f"{pathConfig.reward_learning_data_path}{os.sep}gantt.csv",
                                 index=True)

    @classmethod
    def job_gantt_for_Q_time(cls):
        df = pd.concat([cls.gantt_history_arrival_and_due, cls.gantt_history], ignore_index=True)
        df = df.sort_values(by=['Start', "Finish"], ascending=[False, False])
        df = cls.to_top_arrival_df(df)
        df = cls.to_bottom_due_df(df)
        fig8 = px.timeline(df, x_start="Start", x_end="Finish", y="JOB_ID", template="simple_white", color="Q_check",
                           color_discrete_sequence=px.colors.qualitative.Dark24, text="Q_diff", width=2000, height=2000)
        [(cls.modify_width(bar, 0.7), cls.modify_text(bar))
         for bar in fig8.data if ('setup' in bar.legendgroup)]
        fig8.show()

    @classmethod
    def modify_width(cls, bar, width):
        """
        막대의 너비를 설정합니다.
        width = (단위 px)
        """
        bar.width = width

    @classmethod
    def modify_text(cls, bar):
        """
        막대의 텍스트를 설정합니다.
        width = (단위 px)
        """
        bar.text = "su"


    @classmethod
    def to_top_arrival_df(cls, df):
        """
        figure의 경우 위에서 부터 bar 생성됩니다.
        track_in event를 df(데이터프레임) 가장 밑 행으로 배치시킵니다.
        이 작업을 통해 TRACK_IN 이벤트가 다른 중복되는 차트에 가려지는 것을 방지합니다.
        """
        arrival_df = df.loc[df['Type'] == 'job_arrival']
        df = df[df['Type'] != 'job_arrival']
        arrival_df = pd.concat([arrival_df, df], ignore_index=True)
        return arrival_df

    @classmethod
    def to_bottom_setup_df(cls, df):
        """
        figure의 경우 위에서 부터 bar 생성됩니다.
        track_in event를 df(데이터프레임) 가장 밑 행으로 배치시킵니다.
        이 작업을 통해 TRACK_IN 이벤트가 다른 중복되는 차트에 가려지는 것을 방지합니다.
        """
        setup_df = df.loc[df['Type'] == 'setup']
        df = df[df['Type'] != 'setup']
        df = pd.concat([df, setup_df], ignore_index=True)
        return df

    @classmethod
    def to_bottom_due_df(cls, df):
        """
        figure의 경우 위에서 부터 bar 생성됩니다.
        track_in event를 df(데이터프레임) 가장 밑 행으로 배치시킵니다.
        이 작업을 통해 TRACK_IN 이벤트가 다른 중복되는 차트에 가려지는 것을 방지합니다.
        """
        setup_df = df.loc[df['Type'] == 'due_date']
        df = df[df['Type'] != 'due_date']
        df = pd.concat([df, setup_df], ignore_index=True)
        return df

    @classmethod
    def modify_color(cls, bar):
        bar.marker.color = "#000000"

    @classmethod
    def csv_to_gantt_chart(cls):
        """
        아마도 json으로 변형하면서 datetime type이 int로 바뀐듯 함
        :param datasetId:
        :param num:
        :param event_count:
        :return:
        """
        cls.gantt_history = cls.gantt_history.sort_values(by='Resource')
        df = cls.gantt_history
        # df_base['Traj'] = ['old' if step <= lower_bound else 'new' for step in df['Step']]

        fig_csv = px.timeline(df, x_start="Start", x_end="Finish", y="Resource",
                              color="Type", color_discrete_map=cls.color_by_color_mapper, width=2000,
                              height=800,
                              pattern_shape="Traj", pattern_shape_map={"old": "", "new": "/"})

        [(cls.modify_width(bar, 0.7), cls.modify_text(bar), (cls.modify_color(bar)))
         for bar in fig_csv.data if ('setup' in bar.legendgroup)]

        return fig_csv