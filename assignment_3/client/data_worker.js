const inputElement = document.getElementById("img-upload");
inputElement.addEventListener("change", handleFile, false);


function handleFile() {
    const fileList = this.files;

    //add img to html
    showOriginalImage(fileList[0]);

    //send img to server
    const formData = new FormData();
    formData.append("image", fileList[0]);

    const pendingSpan = document.getElementById("pending");
    pendingSpan.style.visibility = "visible";

    let promise = new Promise(function (resolve, reject) {
        $.ajax({
            type: "POST",
            contentType: false,
            processData: false,
            cache: false,
            url: window.location.href + "handle_img",
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
            // const base64_img = JSON.parse(data)['image'];
            const img = document.createElement("img");
            img.classList.add("obj");
            img.height = 600;
            img.width = 500;
            img.class = "img-fluid";
            img.src = window.location.href + 'uploaded_images/' + fileList[0].name;//img.src = "data:image/png;base64," + base64_img;
            document.getElementById('cont').appendChild(img);
            pendingSpan.style.visibility = "hidden";
        }
    ).catch(function (err) {
        console.log("can't upload image: " + err);
    });
}

function showOriginalImage(file) {
    document.getElementById('cont').innerHTML = "";
    const img = document.createElement("img");
    img.classList.add("obj");
    img.file = file;
    img.height = 600;
    img.width = 500;
    img.class = "img-fluid";
    document.getElementById('cont').appendChild(img);
    const reader = new FileReader();
    reader.onload = (function (aImg) {
        return function (e) {
            aImg.src = e.target.result;
        };
    })(img);
    reader.readAsDataURL(file);
}

