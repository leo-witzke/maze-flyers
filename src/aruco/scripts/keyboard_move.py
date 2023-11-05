#!/usr/bin/python2

import rospy 
from gazebo_msgs.msg import ModelState, ModelStates
from gazebo_msgs.srv import SetModelState
from geometry_msgs.msg import Pose, Twist
import tf

model_name = "camera"
current_pose = Pose()
scale_factor = 0.05

def to_quaternion(rpy):
    return tf.transformations.quaternion_from_euler(rpy[0], rpy[1], rpy[2])

def to_rpy(quaternion):
    return tf.transformations.euler_from_quaternion((
        quaternion[0],
        quaternion[1],
        quaternion[2],
        quaternion[3],
    ))

def set_pose(model_states):
    global current_pose
    for i in range(len(model_states.name)):
        if model_states.name[i] == model_name:
            current_pose = model_states.pose[i]

def keyboard_input(input_twist):
    state_msg = ModelState()
    state_msg.model_name = model_name
    state_msg.pose.position.x = current_pose.position.x + input_twist.linear.x*scale_factor
    state_msg.pose.position.y = current_pose.position.y + input_twist.linear.y*scale_factor
    state_msg.pose.position.z = current_pose.position.z + input_twist.linear.z*scale_factor

    current_rotation = to_rpy([
        current_pose.orientation.x,
        current_pose.orientation.y,
        current_pose.orientation.z,
        current_pose.orientation.w
    ])
    new_rotation = [
        current_rotation[0]+input_twist.angular.x*scale_factor,
        current_rotation[1]+input_twist.angular.y*scale_factor,
        current_rotation[2]+input_twist.angular.z*scale_factor
    ]
    new_rotation_quant = to_quaternion(new_rotation)

    state_msg.pose.orientation.x = new_rotation_quant[0]
    state_msg.pose.orientation.y = new_rotation_quant[1]
    state_msg.pose.orientation.z = new_rotation_quant[2]
    state_msg.pose.orientation.w = new_rotation_quant[3]

    set_state(state_msg)

if __name__ == '__main__':
    rospy.init_node('move_camera')

    rospy.wait_for_service('/gazebo/set_model_state')
    set_state = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)

    rospy.Subscriber("/gazebo/model_states", ModelStates, set_pose)
    rospy.Subscriber("/cmd_vel", Twist, keyboard_input)

    rospy.spin()