const cart_btn = document.querySelector(".cart_btn")
const wish_btn = document.querySelector(".wish_btn")
const buy_btn = document.querySelector(".buy_btn")

const quan = (id) => {
  return document.querySelectorAll('input[type=number]')[id-1].value
}

const check = async(name,image,price,quantity,category,type,productCount,jinja) => {
  quantity = quantity[0] === 'j' ? 1 : quan(parseInt(quantity))
  console.log(name,image,price,quantity,category,type,productCount,jinja)
  await fetch("/add-cart",{
    method : 'POST',
    headers:{
      'content-type':'application/json'
    },
    body : JSON.stringify({name,image,price,quantity,category,type,productCount,jinja})
  })
  .then(res => res.json())
  .then((data) => {
    alert("Successfully added to cart!")
  }).catch((e) => {
    console.log(e)
  })
}