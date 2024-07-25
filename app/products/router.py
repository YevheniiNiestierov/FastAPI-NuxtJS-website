from fastapi import HTTPException, APIRouter

from app.products.crud import insert_new_product, get_product, get_products, delete_item
from app.products.schemas import CreateProduct, ProductFlavour, ProductType

router = APIRouter(
    tags=["Products"],
    prefix="/product"
)


@router.get("/flavours/", response_model=ProductFlavour)
def get_flavours():
    return ProductFlavour()


@router.get("/types/", response_model=ProductType)
def get_types():
    return ProductType()


@router.post("/create_product/")
def create_product(product: CreateProduct):
    return insert_new_product(product.product_type, product.title, product.description, product.price, product.flavour, product.weight)


@router.get("/products/{product_id}")
def get_product_by_id(product_id: str):
    product = get_product(str(product_id))
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products")
def get_all_products():
    return get_products()


# @router.patch("/products/{product_id}")
# def update_product(product_id: uuid.UUID, attribute_name, attribute_value):
#     return update_product_attribute(str(product_id), attribute_name, attribute_value)


# @router.patch("/products/{product_id}", response_model=schemas.Product)
# def update_product(product_id: uuid.UUID,
#                    db: Session = Depends(get_db),
#                    new_title: str | None = None,
#                    new_description: str | None = None,
#                    new_price: int | None = None,
#                    new_weight: int | None = None):
#
#     product = crud.get_product_by_id(db, product_id)
#
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return crud.update_product(db, product, new_title, new_description, new_price, new_weight)
#
#
@router.delete("/products/{product_id}")
def delete_by_id(product_id):
    return delete_item(product_id)

