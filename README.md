# A Basic Visual Regression Test

Here's how you can get this to run:

1. Clone this repo into viregtest/.
`$ cd viregtest`

2. Create a new virtual environment.
`$ python3 -m venv .`

3. Activate the virtual environment.
`$ source bin/activate`

4. Install all the packages you need.
`$  cat requirements.txt  | xargs pip3 install`

5. Install chromedriver.
`$ wget https://chromedriver.storage.googleapis.com/99.0.4844.51/chromedriver_linux64.zip && unzip chromedriver_linux64.zip`

6. Make sure the chromedriver binary is in your path.
`$ export PATH=$PATH:$(pwd)`

7. Run it!
`$ python3 main.py`

