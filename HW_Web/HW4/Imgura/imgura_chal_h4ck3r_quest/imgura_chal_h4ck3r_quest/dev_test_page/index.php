<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css">
  <script defer src="https://use.fontawesome.com/releases/v5.3.1/js/all.js"></script>
  <title>Imgura</title>
</head>

<body>
  <section class="hero is-info is-large">
    <div class="hero-head">
      <nav class="navbar">
        <div class="container">
          <div class="navbar-brand">
            <a class="navbar-item" href="?page=pages/main">
              Imgura
            </a>
            <span class="navbar-burger" data-target="navbarMenuHeroB">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </div>
          <div id="navbarMenuHeroB" class="navbar-menu">
            <div class="navbar-end">
              <a class="navbar-item is-active" href="?page=pages/main">
                Home
              </a>
              <a class="navbar-item" href="#">
                Random Image
              </a>
              <span class="navbar-item">
                <a class="button is-info is-inverted" href="?page=pages/share">
                  <span class="icon">
                    <i class="fas fa-upload"></i>
                  </span>
                  <span>Share</span>
                </a>
              </span>
            </div>
          </div>
        </div>
      </nav>
    </div>

    <div class="hero-body">
      <?php
      include ($_GET['page'] ?? 'pages/main') . ".php";
      ?>
    </div>
  </section>
</body>

</html>