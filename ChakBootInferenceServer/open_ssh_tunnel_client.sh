while true; do
  ssh -N -R localhost:8086:localhost:8086 goldenmine@home.goldenmine.kr
  sleep 1
  echo "restart"
done
