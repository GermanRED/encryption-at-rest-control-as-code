# encryption-at-rest-control-as-code

Source code supporting the blog post
[https://www.german.red/2025/03/01/control-testing-as-code/](https://www.german.red/2025/03/01/control-testing-as-code/)

The project requires [uv](https://docs.astral.sh/uv/) to be installed.

## Running the tests

For simplicity I have included a `Makefile`. Just run `$ make test` and you will see that
we evaluate if an s3 bucket and a database are encrypted at rest. It is as easy as that!

The tests are by default mocked with the great library [moto](https://docs.getmoto.org).
If you want to test it against your own infrastructure, do the following:

 1. Login with the `aws` command to have a valid session token
 2. Run the tests disabling the mocks:

 > $ AWS_MOCKED="false" make test

As usual, test first with a non-production account.
