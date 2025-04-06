---
url: https://hackattic.com/challenges/visual_basic_math
code_url: https://github.com/hitanshu-dhawan/Hackattic
---

# Visual basic math

We need to get some things calculated, so let's get to work.

Hit the problem endpoint and grab the image URL. The image will be a few lines of numbers and operations that you need to perform. Start with `0`, go from top to bottom and figure out the final result. Careful! The numbers may get big. Make sure nothing overflows along the way.

To illustrate, an image roughly equivalent to:

```
+ 12 
- 10  
× 2
```

Should be treated as `(((0 + 12) - 10) × 2)` which equals `4`.

_A word on division:_ for `÷`, the challenge uses floor division which may be slightly surprising. Floor division means that after dividing the numbers, the result is rounded **down**. This means that `-10 ÷ 3` is equal `-4` (the `floor` of `-3.(3)` is `-4`)! Keep this quirk in mind.

Submit the final result the the solution endpoint. It's done!

##### Getting the problem set

`GET /challenges/visual_basic_math/problem?access_token=<access_token>`

Problem JSON:

- `image_url`: the URL of the image we want you to process

##### Submitting a solution

`POST /challenges/visual_basic_math/solve?access_token=<access_token>`

Solution JSON structure:

- `result`: the result of all the math

##### Why this challenge?

It's always interesting to make a computer really read things.

---
# Solution

### Solution 1

```python
client = OpenAI()
response = client.chat.completions.create(
	model="gpt-4o-mini",
	messages=[{
		"role": "user",
		"content": [
			{"type": "text", "text": "Ensure the extracted text consists only of the characters '0123456789+-×÷' while preserving the original formatting. The first character must be one of '+', '-', '×', or '÷', followed by a space, and then a number without any spaces."},
			{
				"type": "image_url",
				"image_url": {
					"url": image_url,
					"detail": "auto",
				}
			},
		],
	}],
)
```

### Solution 2

#Todo

Implement custom local model to extract text from image.
Use approach similar to 'MNIST database of handwritten digits'
Steps:
1. Download multiple images from problem end-point as dataset.
2. Extract digits and operators and label them for dataset.
3. Train the model with good enough accuracy on the above dataset.
4. Use the custom model to extract text and solve the challenge.

---
# Resources

- https://platform.openai.com/docs/guides/images?api-mode=chat&format=url


#Hackattic
