# inbuilt lib imports:
from typing import Dict
import math

# external libs
import tensorflow as tf
from tensorflow.keras import models,layers

# project imports


class CubicActivation(layers.Layer):
    """
    Cubic activation as described in the paper.
    """
    def call(self, vector: tf.Tensor) -> tf.Tensor:
        """
        Parameters
        ----------
        vector : ``tf.Tensor``
            hidden vector of dimension (batch_size, hidden_dim)

        Returns tensor after applying the activation
        """
        # TODO(Students) Start
        # Comment the next line after implementing call.
        
        return vector**3

        #raise NotImplementedError
        # TODO(Students) End


class DependencyParser(models.Model):
    def __init__(self,
                 embedding_dim: int,
                 vocab_size: int,
                 num_tokens: int,
                 hidden_dim: int,
                 num_transitions: int,
                 regularization_lambda: float,
                 trainable_embeddings: bool,
                 activation_name: str = "cubic") -> None:
        """
        This model defines a transition-based dependency parser which makes
        use of a classifier powered by a neural network. The neural network
        accepts distributed representation inputs: dense, continuous
        representations of words, their part of speech tags, and the labels
        which connect words in a partial dependency parse.

        This is an implementation of the method described in

        Danqi Chen and Christopher Manning.
        A Fast and Accurate Dependency Parser Using Neural Networks. In EMNLP 2014.

        Parameters
        ----------
        embedding_dim : ``str``
            Dimension of word embeddings
        vocab_size : ``int``
            Number of words in the vocabulary.
        num_tokens : ``int``
            Number of tokens (words/pos) to be used for features
            for this configuration.
        hidden_dim : ``int``
            Hidden dimension of feedforward network
        num_transitions : ``int``
            Number of transitions to choose from.
        regularization_lambda : ``float``
            Regularization loss fraction lambda as given in paper.
        trainable_embeddings : `bool`
            Is the embedding matrix trainable or not.
        """
        super(DependencyParser, self).__init__()
        self._regularization_lambda = regularization_lambda

        if activation_name == "cubic":
            self._activation = CubicActivation()
        elif activation_name == "sigmoid":
            self._activation = tf.keras.activations.sigmoid
        elif activation_name == "tanh":
            self._activation = tf.keras.activations.tanh
        else:
            raise Exception(f"activation_name: {activation_name} is from the known list.")

        # Trainable Variables
        # TODO(Students) Start

    
        self.embeddings= tf.Variable(tf.random.truncated_normal(shape=[vocab_size,embedding_dim],stddev=0.01))
        self.weight1= tf.Variable(tf.random.truncated_normal(shape=[embedding_dim*num_tokens,hidden_dim],stddev=0.01))
        self.weight2= tf.Variable(tf.random.truncated_normal(shape=[hidden_dim,num_transitions],stddev=0.01))
        self.bias=  tf.Variable(tf.zeros(shape=[1,hidden_dim]))


        

        # TODO(Students) End

    def call(self,
             inputs: tf.Tensor,
             labels: tf.Tensor = None) -> Dict[str, tf.Tensor]:
        """
        Forward pass of Dependency Parser.

        Parameters
        ----------
        inputs : ``tf.Tensor``
            Tensorized version of the batched input text. It is of shape:
            (batch_size, num_tokens) and entries are indices of tokens
            in to the vocabulary. These tokens can be word or pos tag.
            Each row corresponds to input features a configuration.
        labels : ``tf.Tensor``
            Tensor of shape (batch_size, num_transitions)
            Each row corresponds to the correct transition that
            should be made in the given configuration.

        Returns
        -------
        An output dictionary consisting of:
        logits : ``tf.Tensor``
            A tensor of shape ``(batch_size, num_transitions)`` representing
            logits (unnormalized scores) for the labels for every instance in batch.
        loss : ``tf.float32``
            If input has ``labels``, then mean loss for the batch should
            be computed and set to ``loss`` key in the output dictionary.

        """
        # TODO(Students) Start

        embedlookup= tf.nn.embedding_lookup(self.embeddings,inputs)
        #a,b,c a,b*c -reshape
        dimensions= embedlookup.get_shape().as_list()
        embedlookup1=tf.reshape(embedlookup,[dimensions[0],dimensions[1]*dimensions[2]])   
        x= tf.matmul(embedlookup1,self.weight1)+self.bias
        logits=tf.matmul(self._activation.call(x),self.weight2)
        # TODO(Students) End
        output_dict = {"logits": logits}

        if labels is not None:
            output_dict["loss"] = self.compute_loss(logits, labels)
        return output_dict

    def compute_loss(self, logits: tf.Tensor, labels: tf.Tensor) -> tf.float32:
        """
        Parameters
        ----------
        logits : ``tf.Tensor``
            A tensor of shape ``(batch_size, num_transitions)`` representing
            logits (unnormalized scores) for the labels for every instance in batch.

        Returns
        -------
        loss : ``tf.float32``
            If input has ``labels``, then mean loss for the batch should
            be computed and set to ``loss`` key in the output dictionary.

        """
        # TODO(Students) Start

        
        label1 = (labels > -1)
        label1= tf.cast(label1,tf.float32)
        
        result = tf.nn.softmax(logits*label1)

        label2 = (labels == 1)
        label2= tf.cast(label2,tf.float32)
        prod2= result*label2
        result= tf.reduce_sum(prod2,axis= 1)
        loss = tf.reduce_mean(tf.math.log(result)) * -1

        #regularization

        emb=tf.nn.l2_loss(self.embeddings)
        w1= tf.nn.l2_loss(self.weight1)
        w2= tf.nn.l2_loss(self.weight2)
        b= tf.nn.l2_loss(self.bias)

        sumval= emb+w1+w2+b
        regularization= self._regularization_lambda *sumval

        # TODO(Students) End
        return loss + regularization
