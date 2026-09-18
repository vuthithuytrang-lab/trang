add_action( 'init', function () {

	$duong_dan = isset( $_SERVER['REQUEST_URI'] )
		? parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH )
		: '';

	if ( '/sitemap-dich-vu.xml' !== $duong_dan ) {
		return;
	}

	$danh_sach = array(
		array( 'https://www.hr2b.com/vi/', 'weekly', '1.0' ),
		array( 'https://www.hr2b.com/vi/dich-vu/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/vi/dich-vu/dich-vu-tu-van-nhan-su/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/vi/dich-vu/dich-vu-tinh-luong/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/vi/dich-vu/dich-vu-tuyen-dung-cap-cao/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/vi/dich-vu/dich-vu-thue-ngoai-tuyen-dung/', 'monthly', '0.9' ),
		array( 'https://www.hr2b.com/service/hr-consulting/', 'monthly', '0.8' ),
		array( 'https://www.hr2b.com/service/payroll-outsourcing/', 'monthly', '0.8' ),
		array( 'https://www.hr2b.com/service/staffing-outsourcing/', 'monthly', '0.8' ),
		array( 'https://www.hr2b.com/service/executive-search/', 'monthly', '0.8' ),
	);

	$xml  = '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
	$xml .= '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
	foreach ( $danh_sach as $muc ) {
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
