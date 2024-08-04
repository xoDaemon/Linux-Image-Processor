import src.image_mounter as immount
import src.persistence_detector as pdect
import src.config as config
import src.database as db
import src.image as img

def print_title(title):
    print(f'══════════════════╣{title}╠══════════════════')

conf = config.Config()
db = db.Database(conf.db_path)

print_title("MOUNTING IMAGE")
immount.image_mounter(conf.disk_path, conf.phy_mount_path, conf.filesystem_path)

print_title("PROCESSING FILESYSTEM")

db.delete_all()
db.create_tables()

image = img.Image(conf.filesystem_path)
db.insert_image(image)
image.process_file_system()

print('\n')
print_title("IMAGE DETAILS")
image.print_image()

print('\n')
print_title("LOOKING FOR PERSISTENCE")
pdect.persistence_detector(conf.filesystem_path)