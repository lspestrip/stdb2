# REST API

`stdb2` implements a REST API which allows to access programmatically
part of the data in the database via HTTP. Here are its primary features:

- The API only allows to *get* data, i.e., it does not allow to  create/modify/delete entries in the database.
- No need to authenticate.
- All responses are sent as JSON records.

| Address | Meaning |
| ------- | ------- |
| `/unittests/api/bandpass` | List of all the bandpass analyses |
| `/unittests/api/bandpass/NN` | Details about the bandpass analysis with id NN |
| `/unittests/api/spectrum` | List of all the noise spectrum analyses |
| `/unittests/api/spectrum/NN` | Details about the noise spectrum analysis with id NN |
| `/unittests/api/tnoise` | List of all the noise temperature analyses |
| `/unittests/api/tnoise/NN` | Details about the noise temperature analysis with id NN |
| `/unittests/api/countbydate` | Number of tests inserted in the database in the last 30 days |
| `/unittests/api/tests/STRIPNN` | List of all the tests done on polarimeter NN |
| `/unittests/api/tests/types` | List of test types |
| `/unittests/api/tests/types/NN` | List of all the tests with type id equal to NN |
| `/unittests/api/tests/users` | List of users (no sensitive information is included) |

## Examples

This snippet queries the list of tests associated with polarimeter STRIP02:

```python
import requests

d = requests.get("https://striptest.fisica.unimi.it/unittests/api/tests/STRIP02").json()

for test in d:
    print(f"test {test['id']}: {test['description']}")
```

This example shows how to retrieve the list of polarimeters that contain results about bandpass measurements:

```python
import requests

d = requests.get("https://striptest.fisica.unimi.it/unittests/api/bandpass").json()

for pol_name in d["polarimeters"]:
    print(pol_name)
```

Finally, this script prints a table containing the bandpasses (in GHz) of every known polarimeter:

```python
import requests

d = requests.get("https://striptest.fisica.unimi.it/unittests/api/bandpass").json()

for polarimeter_tests in d["results"]:
    for test in polarimeter_tests:
        print(f"{test['polarimeter_name']}: {test['bandwidth_ghz']:.2f} GHz")
```
