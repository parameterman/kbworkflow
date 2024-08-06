from orthocot import BaseWorkflow
import yaml
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    config_file = "./config.yaml"
    patient_info = """姓名：周俞
性别：女
年龄：31
正面：面部左右基本对称，面上1/3偏短
侧面：鼻唇角正常，上下唇后缩，頦部后缩。
口腔检查
一般情况：口腔卫生一般，前牙区可见软垢，牙龈轻微红肿。
正畸专科：1.上下颌拥挤度2/5.5mm，Spee曲线深4mm，上前牙直立，覆盖3.3mm，覆牙合2.3mm。
          2.右侧磨牙I类关系，尖牙III类关系          
          3.Bolton指数前牙比偏大（ 81.3%），全牙比偏小（79.7%）	
X线检查
全景片：   36缺失，38水平阻生。双侧下颌升支长度基本相等，双侧髁状突皮质骨连续。
头影测量：1.骨性II类，高角，颏部后缩，骨性开合。
                 2. 前牙直立，上唇后缩。
正畸专科：1.Spee曲线深4mm，覆盖6.37mm，覆牙合4.41mm双侧spee曲线深度分别为3.75mm/3.5mm。
2.右侧磨牙II类关系，尖牙I类关系          
3.Bolton指数3-3 ：3.Bolton指数3-3 ：81.3%，上颌偏大2.1 mm。6-6比例为79.7%，下颌偏小1.2 mm。
D1:FA点间距离
D2:FA点对应WALA嵴间距离
D1-D2=9MM，左上第一磨牙颊面转矩为-16°，右上第一磨牙颊侧面转矩为-9°左下第一磨牙颊面转矩为-36°，右下第一磨牙颊面转矩为-39°。
X线检查
全景片：14、24缺失，18垂直阻生，左右上颌第⼆恒磨⽛后缘的切线和上颌结节后缘的切线向合平⾯做垂线，两交点之间的距离分别为8.5/8.26mm，双侧下颌升支长度基本相等，双侧髁状突皮质骨连续。
头影测量：1.骨性II类趋势，低角，下颌体平。
          2：颏部前突，上唇突下唇后缩，前牙覆盖深。
下颌侧位片Ceph0L值=8.5mm
Vto处理后切牙目标位与初始位差：
上切牙 (U1)：压低(I)/升高(E), mm: 2 I
唇(La)/舌(Li)向平移, mm: 4.0Li
唇(La)/舌(Li)向转距, °: 4.8La
下切牙 (L1)
压低(I)/升高(E), mm: 2.8 I
唇(La)/舌(Li)向平移, mm: 1.4Li
唇(La)/舌(Li)向转距, °: 0.1 La"""

    config = yaml.safe_load(open(config_file))

    workflow = BaseWorkflow.from_config(config)

    result = workflow.run(input_vars={"patient_info": patient_info})

    print(result)
