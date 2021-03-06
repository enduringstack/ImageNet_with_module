"""
Written by Matteo Dunnhofer - 2017

Definition of AlexNet architecture
"""

import tensorflow as tf
import train_util as tu
import math
from tensorflow.python.training import moving_averages
from tensorflow.python.ops import control_flow_ops
from tensorflow.python.framework import ops

def selu(x,name = "selu"):
    with tf.variable_scope(name):
        alpha = 1.6732632423543772848170429916717
        scale = 1.0507009873554804934193349852946
        return scale * tf.where(x > 0.0, x, alpha * tf.exp(x) - alpha)

def compute_threshold(x):
    # x_max=tf.reduce_max(x,reduce_indices= None, keep_dims= False, name= None)
    x_sum = tf.reduce_sum(tf.abs(x),reduction_indices= None, keep_dims =False ,name= None)
    threshold = tf.div(x_sum,tf.cast(tf.size(x), tf.float32),name= None)
    threshold = tf.multiply(0.7,threshold,name= None)
    return threshold


def compute_alpha(x):
    threshold = compute_threshold(x)
    alpha1_temp1 = tf.where(tf.greater(x,threshold), x, tf.zeros_like(x, tf.float32))
    alpha1_temp2 = tf.where(tf.less(x,-threshold), x, tf.zeros_like(x, tf.float32))
    alpha_array = tf.add(alpha1_temp1,alpha1_temp2,name = None)
    alpha_array_abs = tf.abs(alpha_array)
    alpha_array_abs1 = tf.where(tf.greater(alpha_array_abs,0),tf.ones_like(alpha_array_abs,tf.float32), tf.zeros_like(alpha_array_abs, tf.float32))
    alpha_sum = tf.reduce_sum(alpha_array_abs)
    n = tf.reduce_sum(alpha_array_abs1)
    alpha = tf.div(alpha_sum,n)
    return alpha


def tenary_opration(x):
    """
    Clip and binarize tensor using the straight through estimator (STE) for the gradient.
    """
    g = tf.get_default_graph()

    with ops.name_scope("tenarized") as name:
        with g.gradient_override_map({"Sign": "Identity"}):
            threshold =compute_threshold(x)
            x=tf.sign(tf.add(tf.sign(tf.add(x,threshold)),tf.sign(tf.add(x,-threshold))))
            return x

def cnn(x):
	"""
	AlexNet convolutional layers definition

	Args:
		x: tensor of shape [batch_size, width, height, channels]

	Returns:
		pool5: tensor with all convolutions, pooling and lrn operations applied

	"""
	with tf.name_scope('alexnet_cnn') as scope:
		with tf.name_scope('alexnet_cnn_conv1') as inner_scope:
			wcnn1 = tu.weight([11, 11, 3, 96], name='wcnn1')
			bcnn1 = tu.bias(0.0, [96], name='bcnn1')
			# alpha1 = compute_alpha(wcnn1)
			# wcnn1 = tenary_opration(wcnn1)
			# wcnn1_1 =  tf.multiply(alpha1, wcnn1)
			conv1 = tf.add(tu.conv2d(x, wcnn1, stride=(4, 4), padding='SAME'), bcnn1)
			conv1 = tu.batch_norm(conv1)
			conv1 = selu(conv1)
			# norm1 = tu.lrn(conv1, depth_radius=2, bias=1.0, alpha=2e-05, beta=0.75)
			pool1 = tu.max_pool2d(conv1, kernel=[1, 3, 3, 1], stride=[1, 2, 2, 1], padding='VALID')

		with tf.name_scope('alexnet_cnn_conv2') as inner_scope:
			wcnn2 = tu.weight([5, 5, 96, 256], name='wcnn2')
			wcnn_2 = tu.weight([5, 5, 96, 256], name='wcnn_2')
			bcnn2 = tu.bias(1.0, [256], name='bcnn2')
			alpha2 = compute_alpha(wcnn2)
			pool1 = tf.multiply(pool1, alpha2)
			wcnn_2 = tenary_opration(wcnn2)
			# wcnn_2 = tf.multiply(alpha2, wcnn2)
			conv2 = tf.add(tu.conv2d(pool1, wcnn_2, stride=(1, 1), padding='SAME'), bcnn2)
			conv2 = tu.batch_norm(conv2)
			conv2 = selu(conv2)
			# norm2 = tu.lrn(conv2, depth_radius=2, bias=1.0, alpha=2e-05, beta=0.75)
			pool2 = tu.max_pool2d(conv2, kernel=[1, 3, 3, 1], stride=[1, 2, 2, 1], padding='VALID')

		with tf.name_scope('alexnet_cnn_conv3') as inner_scope:
			wcnn3 = tu.weight([3, 3, 256, 384], name='wcnn3')
			wcnn_3 = tu.weight([3, 3, 256, 384], name= 'wcnn_3')
			bcnn3 = tu.bias(0.0, [384], name='bcnn3')
			alpha3 = compute_alpha(wcnn3)
			wcnn_3 = tenary_opration(wcnn3)
			pool2 = tf.multiply(pool2, alpha3)
			conv3 = tf.add(tu.conv2d(pool2, wcnn_3, stride=(1, 1), padding='SAME'), bcnn3)
			conv3 = tu.batch_norm(conv3)
			conv3 = selu(conv3)

		with tf.name_scope('alexnet_cnn_conv4') as inner_scope:
			wcnn4 = tu.weight([3, 3, 384, 384], name='wcnn4')
			wcnn_4 = tu.weight([3, 3,383, 384], name = 'wcnn_4')
			bcnn4 = tu.bias(1.0, [384], name='bcnn4')
			alpha4 = compute_alpha(wcnn4)
			wcnn_4 = tenary_opration(wcnn4)
			conv3 = tf.multiply(conv3, alpha4)
			conv4 = tf.add(tu.conv2d(conv3, wcnn_4, stride=(1, 1), padding='SAME'), bcnn4)
			conv4 = tu.batch_norm(conv4)
			conv4 = selu(conv4)

		with tf.name_scope('alexnet_cnn_conv5') as inner_scope:
			wcnn5 = tu.weight([3, 3, 384, 256], name='wcnn5')
			wcnn_5 = tu.weight([3, 3, 384, 256], name= 'wcnn_5')
 			bcnn5 = tu.bias(1.0, [256], name='bcnn5')
 			alpha5 = compute_alpha(wcnn5)
			wcnn_5 = tenary_opration(wcnn5)
			conv4 = tf.multiply(conv4, alpha5)
			conv5 = tf.add(tu.conv2d(conv4, wcnn_5, stride=(1, 1), padding='SAME'), bcnn5)
			conv5 = tu.batch_norm(conv5)
			conv5 = selu(conv5)
			pool5 = tu.max_pool2d(conv5, kernel=[1, 3, 3, 1], stride=[1, 2, 2, 1], padding='VALID')

		return pool5

def classifier(x, dropout):
	"""
	AlexNet fully connected layers definition

	Args:
		x: tensor of shape [batch_size, width, height, channels]
		dropout: probability of non dropping out units

	Returns:
		fc3: 1000 linear tensor taken just before applying the softmax operation
			it is needed to feed it to tf.softmax_cross_entropy_with_logits()
		softmax: 1000 linear tensor representing the output probabilities of the image to classify

	"""
	pool5 = cnn(x)

	dim = pool5.get_shape().as_list()
	flat_dim = dim[1] * dim[2] * dim[3] # 6 * 6 * 256
	flat = tf.reshape(pool5, [-1, flat_dim])

	with tf.name_scope('alexnet_classifier') as scope:
		with tf.name_scope('alexnet_classifier_fc1') as inner_scope:
			wfc1 = tu.weight([flat_dim, 4096], name='wfc1')
			wfc_1 = tu.weight([flat_dim, 4096], name='wfc_1')
			bfc1 = tu.bias(0.0, [4096], name='bfc1')
			alpha_full_1 = compute_alpha(wfc1)
			wfc_1 = tenary_opration(wfc1)
			flat = tf.multiply(flat, alpha_full_1)
			fc1 = tf.add(tf.matmul(flat, wfc_1), bfc1)
			fc1 = tu.batch_norm(fc1)
			fc1 = selu(fc1)
			fc1 = tf.nn.dropout(fc1, dropout)

		with tf.name_scope('alexnet_classifier_fc2') as inner_scope:
			wfc2 = tu.weight([4096, 4096], name='wfc2')
			wfc_2 = tu.weight([4096, 4096], name='wfc_2')
			bfc2 = tu.bias(0.0, [4096], name='bfc2')
			alpha6 = compute_alpha(wfc2)
			wfc_2 = tenary_opration(wfc2)
			fc1 = tf.multiply(fc1, alpha6)
			fc2 = tf.add(tf.matmul(fc1, wfc_2), bfc2)
			fc2 = tu.batch_norm(fc2)
			fc2 = selu(fc2)
			fc2 = tf.nn.dropout(fc2, dropout)

		with tf.name_scope('alexnet_classifier_output') as inner_scope:
			wfc3 = tu.weight([4096, 1000], name='wfc3')
			bfc3 = tu.bias(0.0, [1000], name='bfc3')
			# wfc3 = tenary_opration(wfc3)
			fc3 = tf.add(tf.matmul(fc2, wfc3), bfc3)
			softmax = tf.nn.softmax(fc3)

	return fc3, softmax

