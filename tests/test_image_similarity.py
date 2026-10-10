import unittest

from PIL import Image

from ai_exam_monitoring.data.image_similarity import difference_hash, nearest_by_split


class SimilarityTests(unittest.TestCase):
    def test_identical_and_opposite_gradients(self):
        image = Image.new("L", (9, 8))
        image.putdata([x * 25 for _ in range(8) for x in range(9)])
        self.assertEqual(difference_hash(image), difference_hash(image.copy()))
        flipped = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.assertEqual((difference_hash(image) ^ difference_hash(flipped)).bit_count(), 64)

    def test_full_paths_self_exclusion_and_tie_break(self):
        query = {"path": "train/a.jpg", "split": "train", "dhash": 0}
        other = [query, {"path": "valid/a.jpg", "split": "valid", "dhash": 0},
                 {"path": "train/c.jpg", "split": "train", "dhash": 3},
                 {"path": "train/b.jpg", "split": "train", "dhash": 5}]
        result = nearest_by_split(query, other)
        self.assertEqual(result["valid"], {"path": "valid/a.jpg", "distance": 0})
        self.assertEqual(result["train"], {"path": "train/b.jpg", "distance": 2})
        self.assertEqual(nearest_by_split(query, [query]), {})

    def test_uniform_images_collide_not_duplicate_evidence(self):
        self.assertEqual(difference_hash(Image.new("L", (10, 10), 0)),
                         difference_hash(Image.new("L", (10, 10), 255)))
