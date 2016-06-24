<!DOCTYPE html>
<html>
<head>
	<title>It works!</title>
	<h1>Default page for custom python server</h1>
</head>
<body>
	<?php 
		echo 'Yay! PHP works fine.';
		echo '<p> Dump of $_GET is </p> ';
		var_dump($_GET);
		echo '<br>';
		echo '<p> Dump of $_POST is </p>';
		var_dump($_POST);
		echo '<br>';
	?>
	<h2> There is no need to edit this page! </h2>
	<h3> Restart this server in your own base directory. <br> 
		./server.py -d [DIR] <br>
		 Use -h or --help for help
	</h3>
	<form action="#" method="POST"> 
		<span>Insert a value to test POST :-</span>  <input name = "var"> 
		<input type="submit" name="Submitbtn" value="Submit">
	</form>
</body>
</html>
