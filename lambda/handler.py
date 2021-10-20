"""AWS Lambda handler."""

from mangum import Mangum

from hows_my_driving_dc_api.main import app

handler = Mangum(app, lifespan="off")
