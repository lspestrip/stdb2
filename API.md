# REST API

`stdb2` implements a REST API which allows to access programmatically
part of the data in the database via HTTP. Here are its primary features:

- The API only allows to *get* data, i.e., it does not allow to  create/modify/delete entries in the database.
- No need to authenticate.
- All responses are sent as JSON records.

| Address | Meaning |
| ------- | ------- |
| `/unittests/api/tests/bandpass` | List of all the bandpass analyses |
| `/unittests/api/tests/bandpass/NN` | Details about the bandpass analysis with id NN |
| `/unittests/api/tests/spectrum` | List of all the noise spectrum analyses |
| `/unittests/api/tests/spectrum/NN` | Details about the noise spectrum analysis with id NN |
| `/unittests/api/tests/tnoise` | List of all the noise temperature analyses |
| `/unittests/api/tests/tnoise/NN` | Details about the noise temperature analysis with id NN |
| `/unittests/api/tests/countbydate` | Number of tests inserted in the database in the last 30 days |
| `/unittests/api/tests/STRIPNN` | List of all the tests done on polarimeter NN |
| `/unittests/api/tests/STRIPNN` | List of all the tests done on polarimeter NN |
| `/unittests/api/tests/types` | List of test types |
| `/unittests/api/tests/types/NN` | List of all the tests with type id equal to NN |
| `/unittests/api/tests/users` | List of users (no sensitive information is included) |
