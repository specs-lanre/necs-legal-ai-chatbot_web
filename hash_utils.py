import hashlib
class HashUtils:
	"""Utility class for hashing text."""
	@staticmethod
	def sha256(text: str):
		return hashlib.sha256(text.encode("utf-8")).hexdigest()
if __name__ == "__main__":
	text = "Hello World"
	print(HashUtils.sha256(text))
