# flake8: noqa
# pylint: skip-file
DEFAULT_PRE_CONFIG = {
  "characteristics": [
    {
      "key": "reliability",
      "weight": 50,
      "subcharacteristics": [
        {
          "key": "testing_status",
          "weight": 100,
          "measures": [
            {
              "key": "passed_tests",
              "weight": 33
            },
            {
              "key": "test_builds",
              "weight": 33
            },
            {
              "key": "test_coverage",
              "weight": 34
            }
          ]
        }
      ]
    },
    {
      "key": "maintainability",
      "weight": 50,
      "subcharacteristics": [
        {
          "key": "modifiability",
          "weight": 100,
          "measures": [
            {
              "key": "non_complex_file_density",
              "weight": 33
            },
            {
              "key": "commented_file_density",
              "weight": 33
            },
            {
              "key": "duplication_absense",
              "weight": 34
            }
          ]
        }
      ]
    }
  ]
}