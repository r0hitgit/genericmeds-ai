from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ActiveIngredient(Base):
    __tablename__ = "active_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    normalized_name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)

    # Relationships
    product_ingredients = relationship("ProductIngredient", back_populates="ingredient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ActiveIngredient {self.display_name}>"


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("medicine_products.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(Integer, ForeignKey("active_ingredients.id", ondelete="RESTRICT"), nullable=False, index=True)
    strength_value = Column(Float, nullable=False)
    strength_unit = Column(String(50), nullable=False)  # mg, g, mcg, ml, %, etc.
    raw_composition_text = Column(String(500), nullable=True)
    parsing_status = Column(String(50), default="verified", nullable=False)  # verified, uncertain_for_review

    __table_args__ = (
        UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient"),
    )

    # Relationships
    ingredient = relationship("ActiveIngredient", back_populates="product_ingredients")
    product = relationship("MedicineProduct", back_populates="ingredients")

    def __repr__(self):
        return f"<ProductIngredient {self.ingredient.display_name if self.ingredient else self.ingredient_id} {self.strength_value}{self.strength_unit}>"
