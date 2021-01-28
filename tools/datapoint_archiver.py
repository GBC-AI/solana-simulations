import tarfile

base_path = '/mnt/nfs_share/solana/ad160/'

for i in range(81, 82):
    tar = tarfile.open(base_path + str(i) + ".tar.gz", "w:gz")
    tar.add(base_path + str(i), arcname=str(i) + 'tar')
    tar.close()
