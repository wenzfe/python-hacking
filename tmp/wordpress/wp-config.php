<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wp_db' );

/** Database username */
define( 'DB_USER', 'wp_user' );

/** Database password */
define( 'DB_PASSWORD', 'p@ssword' );

/** Database hostname */
define( 'DB_HOST', '127.0.0.1' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         ',y8NXfF5Oly2@[mCtSe,Gl}IGHm~W>myq3oh+`6bQo88Yz_:F1EW(_Ft77G/|K>7' );
define( 'SECURE_AUTH_KEY',  '5di@UK`}`a;9aJ]?=bsyKeyQ4WlL{:yHV4m=H.dl9q-v mArU/=~mdOUa8!YLc:|' );
define( 'LOGGED_IN_KEY',    '{j(riRq7,[m%E&4uFHTA~UpQjz`AZ-<!cB|>[}(yr4A`//i$2ynST?c*IUa*s5pK' );
define( 'NONCE_KEY',        'kw58?6|RLVr.gL~w#14D3l=%*&$ay3s8Sr+hqLtyLd3_Wwt1M! 0[v_B6x3=P;qi' );
define( 'AUTH_SALT',        'IN+C9HU.*hQuq)b%m)tF%)k$*b[yUF,X A4^%gD4OaB:JIDLU)4j:+AlqkMDM*PY' );
define( 'SECURE_AUTH_SALT', '/}V== /5N:!r:E/O$V=ld^H70c>rzgf`|3y+VV8w)T!n5nW)RR:E#1j]v2Mr7y@?' );
define( 'LOGGED_IN_SALT',   'EfRc#7L-o$0VoZ?9t}iXGO>1v8K6uR<zd,PjFfSkLP*{Hnm}4,Ot$kY5ci?W?>YW' );
define( 'NONCE_SALT',       '}J,i``<,rA*^j=n0^5cDsGJc`@K8]VgRx)^BiXl]Q9L@w$:#F&#wgklnkwNGz(~@' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" line. */



/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
