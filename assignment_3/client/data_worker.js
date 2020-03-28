var inputElement = document.getElementById("img-upload");
inputElement.addEventListener("change", handleFile, false);

function handleFile() {
    var fileList = this.files;

    //add img to html
    showOriginalImage(fileList[0]);

    //send img to server
    var formData = new FormData();
    formData.append("image", fileList[0]);

    let promise = new Promise(function (resolve, reject) {
        $.ajax({
            type: "POST",
            contentType: false,
            processData: false,
            cache: false,
            url: "http://127.0.0.1:5000/handle_img",
            data: formData,
            success: function (data) {
                resolve(data);
            },
            error: function (err) {
                reject(err);
            }
        });
    });

    promise.then(function (data) {
            console.log("got response");
            base64_img = JSON.parse(data)['image'];
            var img = document.createElement("img");
            img.classList.add("obj");
            img.height = 300;
            img.width = 250;
            img.style = "display: block";
            img.src = "data:image/png;base64," + base64_img;
            document.getElementById('cont').appendChild(img);
        }
    ).catch(function (err) {
        console.log("can't upload image: " + err);
    });
}

function toHexString(byteArray) {
    return Array.from(byteArray, function (byte) {
        return ('0' + (byte & 0xFF).toString(16)).slice(-2);
    }).join('')
}

function showOriginalImage(file) {
    var img = document.createElement("img");
    img.classList.add("obj");
    img.file = file;
    img.height = 150;
    img.width = 150;
    img.style = "display: block"
    document.getElementById('cont').appendChild(img);
    var reader = new FileReader();
    reader.onload = (function (aImg) {
        return function (e) {
            aImg.src = e.target.result;
        };
    })(img);
    reader.readAsDataURL(file);
}

