/**
 * Sitemap bo sung cho hr2b.com: trang chu tieng Viet + toan bo trang Dich vu.
 * Phan 1: tra noi dung tai /sitemap-dich-vu.xml
 * Phan 2: khai ten no vao trong sitemap_index.xml cua Rank Math
 */

function hr2b_danh_sach_sitemap_bo_sung() {
	return array(
		array( 'https://www.hr2b.com/vi/', 'weekly', '1.0' ),
		array( 'https://www.hr2b.com/vi/dich-vu/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/vi/dich-vu/dich-vu-tu-van-nhan-su/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/vi/dich-vu/dich-vu-tinh-luong/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/vi/dich-vu/dich-vu-tuyen-dung-cap-cao/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/vi/dich-vu/dich-vu-thue-ngoai-tuyen-dung/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/danh-muc-dich-vu/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/service/hr-consulting/', 'monthly', '0.8' ),
		array( 'https://www.hr2b.com/service/payroll-outsourcing/', 'monthly', '0.8' ),
		array( 'https://www.hr2b.com/service/staffing-outsourcing/', 'monthly', '0.8' ),
		array( 'https://www.hr2b.com/service/executive-search/', 'monthly', '0.8' ),
	);
}

/* --- Phan 1 --- */
add_action( 'init', function () {

	$duong_dan = isset( $_SERVER['REQUEST_URI'] )
		? parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH )
		: '';

	if ( '/sitemap-dich-vu.xml' !== $duong_dan ) {
		return;
	}

	$xml  = '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
	$xml .= '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
	foreach ( hr2b_danh_sach_sitemap_bo_sung() as $muc ) {
		$xml .= "\t<url><loc>" . esc_url( $muc[0] ) . '</loc>'
			. '<changefreq>' . $muc[1] . '</changefreq>'
			. '<priority>' . $muc[2] . '</priority></url>' . "\n";
	}
	$xml .= '</urlset>';

	if ( ! headers_sent() ) {
		header( 'Content-Type: application/xml; charset=UTF-8' );
		header( 'X-Robots-Tag: noindex, follow', true );
	}

	echo $xml;
	exit;
}, 1 );

/* --- Phan 2 --- */
add_filter( 'rank_math/sitemap/index', function ( $noi_dung ) {
	$noi_dung .= "\t<sitemap>\n"
		. "\t\t<loc>https://www.hr2b.com/sitemap-dich-vu.xml</loc>\n"
		. "\t\t<lastmod>" . gmdate( 'Y-m-d\TH:i:s+00:00' ) . "</lastmod>\n"
		. "\t</sitemap>\n";
	return $noi_dung;
} );
