<?php
    /* DB 연결 정보*/
    $host = "localhost";
    $user = "tkddn4508";
    $pw = "gom20726!";
    $dbName = "tkddn4508";
    $conn = mysqli_connect($host, $user, $pw, $dbName);
    $Completion = false;
    /* DB 연결 확인 */
    if($conn){ // 연결 성공
        /* DB SELECT*/
        $name = "이상우";//$_POST['name'];
        $student_num = 20230001;//$_POST['student_name'];
        $error_count = "{error_count : 1}";//$_POST['error_count'];
        $MSG = "반갑습니다.";$_POST['MSG']; 
        $MSG_TF = 0;//$_POST['MSG_TF'];

        $stmt = $conn->prepare("SELECT COUNT(*) AS count FROM Student WHERE name = ? AND student_num = ?");
        $stmt->bind_param("si", $name, $student_num);
        $stmt->execute();
        $result = $stmt->get_result();
        $row = mysqli_fetch_array($result);
        if ($row['count'] == 0) {
            $stmt = $conn->prepare("INSERT INTO Student (name, student_num, error_count, MSG, MSG_TF) VALUES (?, ?, ?, ?, ?)");
            $stmt->bind_param("sissi", 
                $name, 
                $student_num, 
                $error_count, 
                $MSG, 
                $MSG_TF
            );
            if($stmt->execute()){
                $Completion = true;
                $idx = mysqli_insert_id($conn);
            }else{
                $Completion = false;
            }
        }
        if($Completion == true){
            $json = json_encode(array("result" => 'success', "msg" => 'success', "name" => $name, "student_num" => $student_num, "error_count" => $error_count, "MSG" => $MSG, "MSG_TF" => $MSG_TF,"idx" =>$idx));
        }else{
            $json = json_encode(array("result" => 'fail', "msg" => 'Completion fail'));
        }
        echo($json);
        mysqli_close($conn);
    }else{ // 연결 실패 
        $json = json_encode(array("result" => 'fail', "msg" => 'login fail'));
        echo($json);
    }
?>