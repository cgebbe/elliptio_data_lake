# TODO list

Things I know are poor, but won't fix now

## save

- metadata should be dataclass

## ETL

- terraform: password in parameter store should be encrypted
- lambda: currently each lambda setups its own `MongoClient`, which is very non-performant with high load
  - https://www.mongodb.com/docs/atlas/manage-connections-aws-lambda/
  - https://www.mongodb.com/docs/atlas/manage-connections-aws-lambda/#connection-example
- mongoDB is currently accessible from anywhere (0.0.0.0)
  - For M0 instance I likely need to setup a NAT
  - see https://github.com/AndrewGuenther/fck-nat
  - would cost around 3$/month
- lambda could return a better message
