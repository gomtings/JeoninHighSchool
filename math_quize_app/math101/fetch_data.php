<?php
    /* DB 연결 정보*/
    $host = "localhost"; //139.150.80.81
    $user = "tkddn4508";//enviot
    $pw = "gom20726!";//env194^9*
    $dbName = "tkddn4508";//lock_iot
    $conn = mysqli_connect($host, $user, $pw, $dbName);
    /* DB 연결 확인 */
    if($conn){ // 연결 성공
        $sql = "SELECT * FROM math101";
        $result = mysqli_query($conn, $sql);
        $rows = array();
        while($row = mysqli_fetch_array($result)){
            array_push($rows, $row);
        }
        $json = json_encode(array("result" => 'success', "msg" => 'mysqli_connect success', "row" => $rows));
        echo($json);
        mysqli_close($conn);
    }else{ // 연결 실패 
        $json = json_encode(array("result" => 'fail', "msg" => 'mysqli_connect fail'));
        echo($json);
    }
?>