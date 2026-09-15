import math

from rclpy.node import Node

from geometry_msgs.msg import PoseStamped

from langchain_core.tools import tool


class ROSGoalPublisher(Node):

    def __init__(self):
        super().__init__("llm_goal_publisher")

        self.publisher = self.create_publisher(PoseStamped,"/goal_pose",10)
        #Erstelle einen Publisher, der Nachrichten vom Typ PoseStamped auf dem Topic /goal_pose veröffentlicht.
    #Mein Node veröffentlicht PoseStamped-Nachrichten auf /goal_pose.

    def publish_goal(self, x, y, theta):
        goal = PoseStamped()
        #Hier erzeugen wir eine neue ROS-Nachricht vom Typ geometry_msgs/msg/PoseStamped.

        goal.header.frame_id = "map"
        #die Frame_id sagt ROS -> die Koordinaten x und y beziehen sich auf das Koordinantedsystem map. ##Wieso ist das Koordinatensystem wichtig? map ist die globale Karte, odom = lokale Odometrie, base_link = Roboter selbst
        goal.header.stamp = self.get_clock().now().to_msg()
        #Timestamp = damit wird gespeichert, wann die Nachricht erzeugt wurde.

        goal.pose.position.x = float(x)
        goal.pose.position.y = float(y)
        goal.pose.position.z = 0.0
        #Hier werden die Positionen gesetzt.
        goal.pose.orientation.z = math.sin(theta / 2.0)
        goal.pose.orientation.w = math.cos(theta / 2.0)
        #Ros speichert die Orientierung als Quaternion, 
        self.publisher.publish(goal)
        #Hier findet eigentliche ROS Kommunikation statt. Die Nachricht wird auf dem Topic /goal_pose veröffentlicht.

        return f"Goal published: x={x}, y={y}, theta={theta}"

@tool
def ROS_send_goal(x: float, y: float, theta: float) -> str:
    """
    Verwenden, wenn auf eine Pose gefahren werden soll.

    Übergabeparameter:
    x = X-Koordinate im map frame
    y = Y-Koordinate im map frame
    theta = Orientierung als Yaw-Winkel in Radiant

    Sendet ein Navigationsziel an ROS2.
    """

    ros_object.publish_goal(x, y, theta)

    return f"Ziel gesendet: x={x}, y={y}, theta={theta}"

#ROS-Node existiert bisher nur als Klasse. Er wurde noch gar nicht gestartet.:
#init_ros ...

