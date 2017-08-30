<?php

$fn  = str_replace("/", "", $_GET['ID']);
$headers = apache_request_headers();

if (isset($headers['If-Modified-Since']) && (strtotime($headers['If-Modified-Since']) == filemtime($fn))) {
	header('Last-Modified: '.gmdate('D, d M Y H:i:s', filemtime($fn)).' GMT', true, 304);
} else {
	header('Last-Modified: '.gmdate('D, d M Y H:i:s', filemtime($fn)).' GMT', true, 200);
	header("Content-Disposition: attachment; filename=" . $imagename);
	header('Content-Length: '.filesize($fn));
	header('Content-Type: image/jpg');
	print file_get_contents($fn);
}

?>

