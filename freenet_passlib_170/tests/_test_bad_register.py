"""helper for method in test_registry.py"""
from freenet_passlib_170.registry import register_crypt_handler
import freenet_passlib_170.utils.handlers as uh

class dummy_bad(uh.StaticHandler):
    name = "dummy_bad"

class alt_dummy_bad(uh.StaticHandler):
    name = "dummy_bad"

# NOTE: if freenet_passlib_170.tests is being run from symlink (e.g. via gaeunit),
#       this module may be imported a second time as test._test_bad_registry.
#       we don't want it to do anything in that case.
if __name__.startswith("freenet_passlib_170.tests"):
    register_crypt_handler(alt_dummy_bad)
