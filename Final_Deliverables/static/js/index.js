const cart_btn = document.querySelector(".cart_btn")
const wish_btn = document.querySelector(".wish_btn")
const buy_btn = document.querySelector(".buy_btn")

const quan = (id) => {
  console.log(id)
  return document.querySelectorAll('input[type=number]')[id-1].value
}

const check = async(id,quantity,type) => {
  quantity = quan(parseInt(quantity))
  console.log(quantity)
  await fetch("/add-cart",{
    method : 'POST',
    headers:{
      'content-type':'application/json'
    },
    body : JSON.stringify({id,quantity,type})
  })
  .then(res => {
    res.json()
  }).then((data) => {
    console.log(data)
  }).catch((e) => {
    console.log(e)
  })
}