<?php
    /* DB 연결 정보*/
    $host = "localhost"; //139.150.80.81
    $user = "tkddn4508";//enviot
    $pw = "gom20726!";//env194^9*
    $dbName = "tkddn4508";//lock_iot
    $conn = mysqli_connect($host, $user, $pw, $dbName);
    $Completion = false
    /* DB 연결 확인 */
    if($conn){ // 연결 성공
        /* DB SELECT*/
        $book_num = $_POST['book_num'];

        $sql = "DELETE FROM book WHERE book_num = $book_num;";
        $result = mysqli_query($conn, $sql);
        $row = mysqli_fetch_array($result);
        $json = json_encode(array("result" => 'success', "msg" => 'success'));
        echo($json);
        mysqli_close($conn);
    }else{ // 연결 실패 
        $json = json_encode(array("result" => 'fail', "msg" => 'login fail'));
        echo($json);
    }
?>