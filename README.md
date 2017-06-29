# Instagram-API-python

Unofficial Instagram API library.

Provides access to Instagrams features, including the unpublished
ones, such as uploading photos and video.

### History

* Instagram provide a published API, but it doesn't include many
features.

* There's a PHP project [Instagram-API](https://github.com/mgp25/Instagram-API) to reverse-engineer the
interface used by the Instagram App on your phone. It is a useful resource, and a result of careful work. Changes to the API may take time to be reflected here.

* There's an initial Python port of that project, [LevPasha/Instagram-API-python](https://github.com/LevPasha/Instagram-API-python). It doesn't have a complete set of end-points, and changes to the PHP version may take time to be reflected here.

* This is a fork of that project, in an attempt to make it more robust (exceptions, logging), cleaner (iterators, simplifying interfaces), and compliant with coding standards. Changes to the other port version may take time to be reflected here.

   * There are already some breaking changes, and are likely to be more, but clients of Lev Pasha's project will find the changes required to use this library are minor.

As a result, please be aware that this project will always be behind and incomplete when it comes to Instagram's new features.


### Installation Instructions

1. Fork/Clone/Download this repo

    `git clone https://github.com/Julian-O/Instagram-API-python.git`


2. Navigate to the directory

    `cd Instagram-API-python`


3. Install the dependencies

    `pip install -r requirements.txt`


4. If you want to run the examples or tests:

  * Create a file in the
   InstagramAPI directory called `credentials.py`, which contains:

     ````
   USERNAME = "your_instagram_user_name"
   PASSWORD = "your_instagram_password"
   ````

  * Run the test script.

    `python test.py`
