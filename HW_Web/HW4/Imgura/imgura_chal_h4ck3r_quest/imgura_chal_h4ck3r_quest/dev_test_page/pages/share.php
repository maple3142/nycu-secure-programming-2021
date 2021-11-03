<div class="container">
    <p class="title">
    Share Your Image Now!
    </p>
    <p class="subtitle">
        Support: png / jpeg / jpg
    </p>
    <form action="upload.php" method="POST" enctype="multipart/form-data">
    <div class="file is-large has-name">
        <label class="file-label">
            <input class="file-input" type="file" name="image_file" onchange="readURL(this)" accept="image/jpeg,image/png">
            <span class="file-cta">
                <span class="file-icon">
                    <i class="fas fa-upload"></i>
                </span>
                <span class="file-label">
                    Select an image...
                </span>
            </span>
            <span class="file-name">
                ...
            </span>
        </label>
    </div>
    <br>
    <button class="button is-inverted is-medium">Upload</button>
    </form>
</div>

<script>
    function readURL(input) {
        if (input.files && input.files[0]) {
            const file = input.files[0];
            console.log(file)
            document.querySelector(".file-name").innerText = file.name;
        } 
    }
</script>