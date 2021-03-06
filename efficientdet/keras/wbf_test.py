from absl import logging
import tensorflow as tf

from keras import wbf


class WbfTest(tf.test.TestCase):

  def test_detection_iou_same(self):
    d1 = tf.constant([[1, 1, 1, 3, 3, 1, 1]], dtype=tf.float32)
    d2 = tf.constant([1, 1, 1, 3, 3, 1, 1], dtype=tf.float32)

    iou = wbf.vectorized_iou(d1, d2)

    self.assertAllClose(iou[0][0], 1.0)

  def test_detection_iou_corners(self):
    d1 = tf.constant([[1, 1, 1, 3, 3, 1, 1]], dtype=tf.float32)
    d2 = tf.constant([1, 2, 2, 4, 4, 1, 1], dtype=tf.float32)

    iou = wbf.vectorized_iou(d1, d2)

    self.assertAllClose(iou[0][0], 1.0 / 7.0)

  def test_detection_iou_ends(self):
    d1 = tf.constant([[1, 1, 1, 3, 2, 1, 1]], dtype=tf.float32)
    d2 = tf.constant([1, 2, 1, 4, 2, 1, 1], dtype=tf.float32)

    iou = wbf.vectorized_iou(d1, d2)

    self.assertAllClose(iou[0][0], 1.0 / 3.0)

  def test_detection_iou_none(self):
    d1 = tf.constant([[1, 1, 1, 3, 3, 1, 1]], dtype=tf.float32)
    d2 = tf.constant([1, 3, 3, 5, 5, 1, 1], dtype=tf.float32)

    iou = wbf.vectorized_iou(d1, d2)

    self.assertAllClose(iou[0][0], 0)

  def test_detection_iou_vector(self):
    vector_to_match = tf.constant(
        [
            [1, 1, 1, 3, 3, 1, 1],
            [1, 2, 2, 4, 4, 1, 1],
            [1, 3, 3, 5, 5, 1, 1],
        ],
        dtype=tf.float32,
    )

    detection = tf.constant([1, 1, 1, 3, 3, 1, 1], dtype=tf.float32)

    ious = wbf.vectorized_iou(vector_to_match, detection)
    self.assertAllClose(tf.reshape(ious, [3]), [1, 1.0 / 7.0, 0])

  def test_find_matching_cluster_matches(self):
    matching_cluster = tf.constant([1, 1, 1, 2, 2, 1, 1], dtype=tf.float32)
    non_matching_cluster = tf.constant([1, 3, 3, 2, 2, 1, 1], dtype=tf.float32)

    box = tf.constant([1, 1, 1, 2, 2, 1, 1], dtype=tf.float32)

    cluster_index = wbf.find_matching_cluster(
        (matching_cluster, non_matching_cluster), box)

    self.assertAllClose(cluster_index, 0)

    cluster_index = wbf.find_matching_cluster(
        (non_matching_cluster, matching_cluster), box)

    self.assertAllClose(cluster_index, 1)

  def test_find_matching_cluster_best_overlap(self):
    overlaps = tf.constant([1, 1, 1, 11, 2, 1, 1], dtype=tf.float32)
    overlaps_better = tf.constant([1, 2, 1, 12, 2, 1, 1], dtype=tf.float32)

    box = tf.constant([1, 3, 1, 13, 2, 1, 1], dtype=tf.float32)

    cluster_index = wbf.find_matching_cluster((overlaps,), box)

    self.assertAllClose(cluster_index, 0)

    cluster_index = wbf.find_matching_cluster((overlaps, overlaps_better), box)

    self.assertAllClose(cluster_index, 1)

  def test_weighted_average(self):
    samples = tf.constant([1, 3], dtype=tf.float32)

    weights1 = tf.constant([0.5, 0.5], dtype=tf.float32)
    weighted_average1 = wbf.weighted_average(samples, weights1)
    
    self.assertAllClose(weighted_average1, 2)

    weights2 = tf.constant([1, 0], dtype=tf.float32)
    weighted_average2 = wbf.weighted_average(samples, weights2)
    
    self.assertAllClose(weighted_average2, 1)

    weights3 = tf.constant([1, 2], dtype=tf.float32)
    weighted_average3 = wbf.weighted_average(samples, weights3)
    
    self.assertAllClose(weighted_average3, 7.0/3.0)

  def test_average_detections(self):
    d1 = tf.constant([1, 1, 1, 2, 2, 0.3, 1], dtype=tf.float32)
    d2 = tf.constant([1, 3, 3, 4, 4, 0.7, 1], dtype=tf.float32)

    averaged = wbf.average_detections((d1, d2))

    self.assertAllClose(averaged, [1, 2.4, 2.4, 3.4, 3.4, 0.5, 1])

  def test_ensemble_boxes(self):
    d1 = tf.constant([1, 2, 1, 10, 1, 0.75, 1], dtype=tf.float32)
    d2 = tf.constant([1, 3, 1, 10, 1, 0.75, 1], dtype=tf.float32)
    d3 = tf.constant([1, 3, 1, 10, 1, 1, 2], dtype=tf.float32)

    ensembled = wbf.ensemble_detections({'num_classes': 3},
                                        tf.stack([d1, d2, d3]))

    self.assertAllClose(ensembled,
                        [[1, 3, 1, 10, 1, 1, 2], [1, 2.5, 1, 10, 1, 0.75, 1]])


if __name__ == '__main__':
  logging.set_verbosity(logging.WARNING)
  tf.test.main()
