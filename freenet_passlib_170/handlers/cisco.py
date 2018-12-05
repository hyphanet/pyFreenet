"""freenet_passlib_170.handlers.cisco - Cisco password hashes"""
#=============================================================================
# imports
#=============================================================================
# core
from binascii import hexlify, unhexlify
from hashlib import md5
import logging; log = logging.getLogger(__name__)
from warnings import warn
# site
# pkg
from freenet_passlib_170.utils import right_pad_string, to_unicode
from freenet_passlib_170.utils.binary import h64
from freenet_passlib_170.utils.compat import unicode, u, join_byte_values, \
             join_byte_elems, iter_byte_values, uascii_to_str
import freenet_passlib_170.utils.handlers as uh
# local
__all__ = [
    "cisco_pix",
    "cisco_type7",
]

#=============================================================================
# cisco pix firewall hash
#=============================================================================
class cisco_pix(uh.TruncateMixin, uh.HasUserContext, uh.StaticHandler):
    """This class implements the password hash used by (older) Cisco PIX firewalls,
    and follows the :ref:`password-hash-api`.
    It does a single round of hashing, and relies on the username
    as the salt.

    The :meth:`~freenet_passlib_170.ifc.PasswordHash.hash`, :meth:`~passlib.ifc.PasswordHash.genhash`, and :meth:`~passlib.ifc.PasswordHash.verify` methods
    have the following extra keyword:

    :type user: str
    :param user:
        String containing name of user account this password is associated with.

        This is *required* in order to correctly hash passwords associated
        with a user account on the Cisco device, as it is used to salt
        the hash.

        Conversely, this *must* be omitted or set to ``""`` in order to correctly
        hash passwords which don't have an associated user account
        (such as the "enable" password).

    :param bool truncate_error:
        By default, this will silently truncate passwords larger than 16 bytes.
        Setting ``truncate_error=True`` will cause :meth:`~freenet_passlib_170.ifc.PasswordHash.hash`
        to raise a :exc:`~freenet_passlib_170.exc.PasswordTruncateError` instead.

        .. versionadded:: 1.7

    .. versionadded:: 1.6
    """
    #===================================================================
    # class attrs
    #===================================================================

    #--------------------
    # PasswordHash
    #--------------------
    name = "cisco_pix"
    setting_kwds = ("truncate_error",)

    #--------------------
    # GenericHandler
    #--------------------
    checksum_size = 16
    checksum_chars = uh.HASH64_CHARS

    #--------------------
    # TruncateMixin
    #--------------------
    truncate_size = 16

    #--------------------
    # custom
    #--------------------

    #: control flag signalling "cisco_asa" mode
    _is_asa = False

    #===================================================================
    # methods
    #===================================================================
    def _calc_checksum(self, secret):

        # This function handles both the cisco_pix & cisco_asa formats:
        #   * PIX had a limit of 16 character passwords, and always appended the username.
        #   * ASA 7.0 (2005) increases this limit to 32, and conditionally appends the username.
        # The two behaviors are controlled based on the _is_asa class-level flag.
        asa = self._is_asa

        # XXX: No idea what unicode policy is, but all examples are
        #      7-bit ascii compatible, so using UTF-8.
        if isinstance(secret, unicode):
            secret = secret.encode("utf-8")
        seclen = len(secret)

        # check for truncation (during .hash() calls only)
        if self.use_defaults:
            self._check_truncate_policy(secret)

        # PIX/ASA: Per-user accounts use the first 4 chars of the username as the salt,
        #          whereas global "enable" passwords don't have any salt at all.
        # ASA only: Don't append user if password is 28 or more characters.
        user = self.user
        if user and not (asa and seclen > 27):
            if isinstance(user, unicode):
                user = user.encode("utf-8")
            secret += user[:4]

        # PIX: null-pad or truncate to 16 bytes.
        # ASA: increase to 32 bytes if password is 13 or more characters.
        if asa and seclen > 12:
            padsize = 32
        else:
            padsize = 16
        secret = right_pad_string(secret, padsize)

        # md5 digest
        hash = md5(secret).digest()

        # drop every 4th byte
        hash = join_byte_elems(c for i,c in enumerate(hash) if i & 3 < 3)

        # encode using Hash64
        return h64.encode_bytes(hash).decode("ascii")

    #===================================================================
    # eoc
    #===================================================================


class cisco_asa(cisco_pix):
    """
    This class implements the password hash used by Cisco ASA/PIX 7.0 and newer (2005).
    Aside from a different internal algorithm, it's use and format is identical
    to the older :class:`cisco_pix` class.

    For passwords less than 13 characters, this should be identical to :class:`!cisco_pix`,
    but will generate a different hash for anything larger
    (See the `Format & Algorithm`_ section for the details).

    Unlike cisco_pix, this will truncate passwords larger than 32 bytes.

    .. versionadded:: 1.7
    """
    #===================================================================
    # class attrs
    #===================================================================

    #--------------------
    # PasswordHash
    #--------------------
    name = "cisco_asa"

    #--------------------
    # TruncateMixin
    #--------------------
    truncate_size = 32

    #--------------------
    # cisco_pix
    #--------------------
    _is_asa = True

    #===================================================================
    # eoc
    #===================================================================

#=============================================================================
# type 7
#=============================================================================
class cisco_type7(uh.GenericHandler):
    """This class implements the Type 7 password encoding used by Cisco IOS,
    and follows the :ref:`password-hash-api`.
    It has a simple 4-5 bit salt, but is nonetheless a reversible encoding
    instead of a real hash.

    The :meth:`~freenet_passlib_170.ifc.PasswordHash.using` method accepts the following optional keywords:

    :type salt: int
    :param salt:
        This may be an optional salt integer drawn from ``range(0,16)``.
        If omitted, one will be chosen at random.

    :type relaxed: bool
    :param relaxed:
        By default, providing an invalid value for one of the other
        keywords will result in a :exc:`ValueError`. If ``relaxed=True``,
        and the error can be corrected, a :exc:`~freenet_passlib_170.exc.PasslibHashWarning`
        will be issued instead. Correctable errors include
        ``salt`` values that are out of range.

    Note that while this class outputs digests in upper-case hexadecimal,
    it will accept lower-case as well.

    This class also provides the following additional method:

    .. automethod:: decode
    """
    #===================================================================
    # class attrs
    #===================================================================

    #--------------------
    # PasswordHash
    #--------------------
    name = "cisco_type7"
    setting_kwds = ("salt",)

    #--------------------
    # GenericHandler
    #--------------------
    checksum_chars = uh.UPPER_HEX_CHARS

    #--------------------
    # HasSalt
    #--------------------

    # NOTE: encoding could handle max_salt_value=99, but since key is only 52
    #       chars in size, not sure what appropriate behavior is for that edge case.
    min_salt_value = 0
    max_salt_value = 52

    #===================================================================
    # methods
    #===================================================================
    @classmethod
    def using(cls, salt=None, **kwds):
        subcls = super(cisco_type7, cls).using(**kwds)
        if salt is not None:
            salt = subcls._norm_salt(salt, relaxed=kwds.get("relaxed"))
            subcls._generate_salt = staticmethod(lambda: salt)
        return subcls

    @classmethod
    def from_string(cls, hash):
        hash = to_unicode(hash, "ascii", "hash")
        if len(hash) < 2:
            raise uh.exc.InvalidHashError(cls)
        salt = int(hash[:2]) # may throw ValueError
        return cls(salt=salt, checksum=hash[2:].upper())

    def __init__(self, salt=None, **kwds):
        super(cisco_type7, self).__init__(**kwds)
        if salt is not None:
            salt = self._norm_salt(salt)
        elif self.use_defaults:
            salt = self._generate_salt()
            assert self._norm_salt(salt) == salt, "generated invalid salt: %r" % (salt,)
        else:
            raise TypeError("no salt specified")
        self.salt = salt

    @classmethod
    def _norm_salt(cls, salt, relaxed=False):
        """
        validate & normalize salt value.
        .. note::
            the salt for this algorithm is an integer 0-52, not a string
        """
        if not isinstance(salt, int):
            raise uh.exc.ExpectedTypeError(salt, "integer", "salt")
        if 0 <= salt <= cls.max_salt_value:
            return salt
        msg = "salt/offset must be in 0..52 range"
        if relaxed:
            warn(msg, uh.PasslibHashWarning)
            return 0 if salt < 0 else cls.max_salt_value
        else:
            raise ValueError(msg)

    @staticmethod
    def _generate_salt():
        return uh.rng.randint(0, 15)

    def to_string(self):
        return "%02d%s" % (self.salt, uascii_to_str(self.checksum))

    def _calc_checksum(self, secret):
        # XXX: no idea what unicode policy is, but all examples are
        # 7-bit ascii compatible, so using UTF-8
        if isinstance(secret, unicode):
            secret = secret.encode("utf-8")
        return hexlify(self._cipher(secret, self.salt)).decode("ascii").upper()

    @classmethod
    def decode(cls, hash, encoding="utf-8"):
        """decode hash, returning original password.

        :arg hash: encoded password
        :param encoding: optional encoding to use (defaults to ``UTF-8``).
        :returns: password as unicode
        """
        self = cls.from_string(hash)
        tmp = unhexlify(self.checksum.encode("ascii"))
        raw = self._cipher(tmp, self.salt)
        return raw.decode(encoding) if encoding else raw

    # type7 uses a xor-based vingere variant, using the following secret key:
    _key = u("dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87")

    @classmethod
    def _cipher(cls, data, salt):
        """xor static key against data - encrypts & decrypts"""
        key = cls._key
        key_size = len(key)
        return join_byte_values(
            value ^ ord(key[(salt + idx) % key_size])
            for idx, value in enumerate(iter_byte_values(data))
        )

#=============================================================================
# eof
#=============================================================================
